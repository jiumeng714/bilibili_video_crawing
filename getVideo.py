"""
用于处理下载视频模块的信息。

2026 修订说明：
B 站升级后，网页里的 window.__playinfo__ 不再稳定（未登录、部分稿件直接没有），
而且 player/playurl 接口强制要求 WBI 签名，旧的正则爬取网页方案已经失效。
现在改为走官方 API：
    x/web-interface/view        -> 视频标题 / UP主 / 封面 / 各分P 的 cid
    x/player/wbi/playurl        -> 音视频流地址（带 WBI 签名，见 wbi.py）
最后仍然用 ffmpeg 把音视频合成到 mp4。
"""

import os
import re
import threading

import ffmpeg  # 处理音频和视频合成

import VideoToAudio as voAuOp  # 视频提取音频操作。
import wbi  # WBI 签名与官方 API 封装
from ffmpegTool import getFfmpegPath, runFfmpeg  # ffmpeg 定位与调用
from jmCommon import loadCookie, safeFileName  # 公共小工具（保留同名导出，方便外部调用）

jm_video_title = 'jm'

# 画质 id 对照表
QUALITY_NAMES = {
    127: '8K 超高清',
    126: '杜比视界',
    125: 'HDR 真彩',
    120: '4K 超清',
    116: '1080P60 高帧率',
    112: '1080P+ 高码率',
    80: '1080P 高清',
    74: '720P60 高帧率',
    64: '720P 高清',
    32: '480P 清晰',
    16: '360P 流畅',
    6: '240P 极速',
}

# 音频 id 对照表
AUDIO_QUALITY_NAMES = {
    30300: '杜比全景声',
    30250: '杜比音频',
    30280: '192K',
    30232: '132K',
    30216: '64K',
}


def describeQuality(qualityId):
    """把画质 id 翻译成人话。"""
    return QUALITY_NAMES.get(qualityId, '未知画质（质量值 {0}）'.format(qualityId))


def describeAudioQuality(qualityId):
    """把音频 id 翻译成人话。"""
    return AUDIO_QUALITY_NAMES.get(qualityId, '质量值 {0}'.format(qualityId))


# --------------------------------------------------------------------------- #
# 工具函数
# --------------------------------------------------------------------------- #
def parseVideoUrl(urlStr):
    """
    从 B 站链接里解析出视频编号与分P。

    支持：
        https://www.bilibili.com/video/BV1B8rPBCELm/?spm_id_from=...
        https://www.bilibili.com/video/BV1B8rPBCELm?p=2
        https://b23.tv/xxxxxx （短链，会自动展开）
        BV1B8rPBCELm / av170001 这样的裸编号

    :return: {'bvid': str 或 None, 'aid': str 或 None, 'p': int 或 None}
    """
    raw = str(urlStr or '').strip()
    if raw == '':
        raise ValueError('视频URL不能为空')

    # 用户可能直接粘贴一整段分享文案，先从中抠出链接
    urlMatch = re.search(r'https?://[^\s，,、）)]+', raw)
    target = urlMatch.group() if urlMatch else raw

    if 'b23.tv' in target:  # 手机端分享出来的短链，需要跟随跳转
        try:
            session = wbi.createSession()
            response = session.get(target, headers=wbi.DEFAULT_HEADERS,
                                   allow_redirects=True, timeout=15)
            target = response.url
        except Exception as error:
            raise ValueError('短链 {0} 展开失败：{1}'.format(target, error))

    result = {'bvid': None, 'aid': None, 'p': None}

    bvMatch = re.search(r'[Bb][Vv][0-9A-Za-z]{10}', target)
    if bvMatch:
        result['bvid'] = bvMatch.group()
    else:
        avMatch = re.search(r'[Aa][Vv](\d+)', target) or re.search(r'[?&]aid=(\d+)', target)
        if avMatch:
            result['aid'] = avMatch.group(1)

    if result['bvid'] is None and result['aid'] is None:
        raise ValueError('没有从「{0}」里找到 BV 号或 av 号，请检查链接'.format(raw))

    pMatch = re.search(r'[?&]p=(\d+)', target)
    if pMatch:
        result['p'] = int(pMatch.group(1))

    return result


# 通过url字符串拆分出对应的BV号（保留原函数名，封面相关的界面代码还在用它）
def getBVbyUrl(urlStr):
    parsed = parseVideoUrl(urlStr)
    if parsed['bvid']:
        return parsed['bvid']
    return 'av' + parsed['aid']


def splitBvAndPage(bvNo):
    """
    兼容旧的调用方式：BV 号后面可能带着 '?p=9'。
    :return: (bvid 或 av号, 分P 或 None)
    """
    text = str(bvNo).strip()
    page = None
    if '?' in text:
        text, query = text.split('?', 1)
        pMatch = re.search(r'p=(\d+)', query)
        if pMatch:
            page = int(pMatch.group(1))
    text = text.replace('/', '')
    return text, page


def write_res(filename, data, path):
    """
    写入信息到对应文件夹（保留原函数，供需要一次性写字节的场景使用）。
    :param filename: 文件名称
    :param data: 数据
    :param path: 文件路径
    :return:
    """
    with open(os.path.join(path, filename), 'wb') as fileObj:
        fileObj.write(data)


# --------------------------------------------------------------------------- #
# 音视频流挑选与下载
# --------------------------------------------------------------------------- #
def pickVideoStream(playData):
    """
    从 playurl 返回的数据里挑一路画质最高的视频流。
    同样画质下优先 AVC(H.264, codecid=7)，兼容性最好；没有再退到 HEVC/AV1。
    :return: (stream_dict, error_msg)
    """
    dash = playData.get('dash') or {}
    videos = dash.get('video') or []
    if not videos:
        return None, '该视频没有可用的 dash 视频流'
    bestQuality = max(video['id'] for video in videos)
    sameQuality = [video for video in videos if video['id'] == bestQuality]
    sameQuality.sort(key=lambda video: 0 if video.get('codecid') == 7 else 1)
    return sameQuality[0], None


def pickAudioStream(playData):
    """
    挑一路码率最高的音频流。
    :return: (stream_dict, error_msg)
    """
    dash = playData.get('dash') or {}
    audios = dash.get('audio') or []
    if not audios:
        return None, '该视频没有可用的 dash 音频流'
    return max(audios, key=lambda audio: audio.get('id', 0)), None


def streamUrls(stream):
    """
    把 base_url 与 backup_url 合成一个候选列表，前面的挂了就用后面的。
    """
    urls = []
    if stream.get('base_url'):
        urls.append(stream['base_url'])
    for backup in stream.get('backup_url') or []:
        if backup not in urls:
            urls.append(backup)
    return urls


def downloadStream(session, urls, outPath, tk_text=None, label='', kind=''):
    """
    流式下载m4s音视频流，边下边写盘，避免几十上百兆的内容全部堆在内存里。
    :param urls: 候选地址列表（含备用地址）
    :return: 出错信息，成功返回 None
    """
    if not urls:
        return '没有可用的下载地址，可能是播放地址已过期，请重新下载'
    lastError = ''
    for url in urls:
        tmpPath = outPath + '.part'
        try:
            with session.get(url, headers=wbi.DEFAULT_HEADERS, stream=True, timeout=30) as response:
                response.raise_for_status()
                total = int(response.headers.get('Content-Length') or 0)
                written = 0
                step = 0
                with open(tmpPath, 'wb') as fileObj:
                    for chunk in response.iter_content(chunk_size=1024 * 256):
                        if not chunk:
                            continue
                        fileObj.write(chunk)
                        written += len(chunk)
                        if tk_text is not None and total:
                            percent = int(written * 100 / total)
                            if percent >= step + 10:
                                step = percent // 10 * 10
                                tk_text.insert(
                                    'end',
                                    '【{0}】{1}下载中...{2}%（{3:.1f}MB/{4:.1f}MB）\n'.format(
                                        label, kind, percent,
                                        written / 1048576, total / 1048576))
                                tk_text.see('end')
            if os.path.exists(outPath):
                os.remove(outPath)
            os.replace(tmpPath, outPath)
            return None
        except Exception as error:
            lastError = str(error)
            if os.path.exists(tmpPath):
                try:
                    os.remove(tmpPath)
                except OSError:
                    pass
            continue
    return lastError


# --------------------------------------------------------------------------- #
# 音视频合成
# --------------------------------------------------------------------------- #
def video_audio_merge_ffmpeg(video_name, filePath):
    """
    合并音频和视频。视频流直接 -c:v copy 不重新编码（旧版本重新编码又慢又掉画质），
    音频转成 AAC 保证 mp4 容器兼容。
    :param video_name: 视频名称（不含后缀）
    :param filePath: 指定的输出路径
    :return: 合成后的文件完整路径
    """
    videoPath = os.path.join(filePath, video_name + '.video.m4s')
    audioPath = os.path.join(filePath, video_name + '.audio.m4s')
    outputPath = os.path.join(filePath, video_name + '_jm.mp4')
    if os.path.exists(outputPath):  # 已存在就先删掉，避免 ffmpeg 询问是否覆盖
        os.remove(outputPath)

    try:
        runFfmpeg([
            '-y',
            '-i', videoPath,
            '-i', audioPath,
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart',
            outputPath,
        ], errorTip='ffmpeg 合成失败')
        if not os.path.exists(outputPath):
            raise RuntimeError('ffmpeg 合成失败：没有生成输出文件')
    except FileNotFoundError:
        # 没找到 ffmpeg 时退回 ffmpeg-python（与其他环境兼容）
        audio_file = ffmpeg.input(audioPath)
        video_file = ffmpeg.input(videoPath)
        ffmpeg.output(audio_file, video_file, outputPath,
                      vcodec='copy', acodec='aac').overwrite_output().run()

    print('音视频合成结束')
    # 删除分离前的视频和音频
    for tmpFile in (videoPath, audioPath):
        if os.path.exists(tmpFile):
            os.remove(tmpFile)
    return outputPath


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def getVideoByBV(bvNo, path, global_dict, isOnlyAudio=False, pageNum=None, wait=False):
    """
    通过 BV 号爬取视频（或只爬取音频）。
    :param bvNo: BV 号，允许带 '?p=9' 这样的分P信息
    :param path: 输出目录
    :param global_dict: 方便输出信息到text框
    :param isOnlyAudio: 默认输出视频，如果只要音频，将该值改为True
    :param pageNum: 分P 序号，从 1 开始
    :param wait: 是否等待下载完成（界面里要 False，别把界面卡死；命令行里用 True）
    :return: path
    """
    bvId, pageInBv = splitBvAndPage(bvNo)
    if pageNum is None:
        pageNum = pageInBv or 1

    def work():
        tk_text = global_dict.get('text')  # 主输出台的text文本框
        tk_text.tag_config('jiumeng2', foreground='red')
        tk_text.tag_config('zhl', foreground='deeppink')
        tk_text.tag_config('nice', foreground='#281285')

        tk_text.insert('end', '获取到的视频编号为:' + bvId + '\n')
        tk_text.see('end')

        session = wbi.createSession(loadCookie())

        # 1. 视频基本信息
        if bvId.lower().startswith('av'):
            info, error = wbi.getVideoInfo(session, aid=bvId[2:])
        else:
            info, error = wbi.getVideoInfo(session, bvid=bvId)
        if error is not None:
            tk_text.insert('end', error + '\n', 'jiumeng2')
            tk_text.see('end')
            return

        pages = info.get('pages') or [{'cid': info.get('cid'), 'page': 1, 'part': info.get('title')}]
        if pageNum < 1 or pageNum > len(pages):
            tk_text.insert(
                'end',
                '分P 超出范围：该视频一共 {0} 个分P，你却要第 {1} 个\n'.format(len(pages), pageNum),
                'jiumeng2')
            tk_text.see('end')
            return
        page = pages[pageNum - 1]
        cid = page.get('cid') or info.get('cid')

        # 2. 组装文件名：[UP主] - 标题 （多分P 时带上分P名）
        title = '[{0}] - {1}'.format(
            info.get('owner', {}).get('name', 'unknown'), info.get('title', ''))
        if len(pages) > 1 and page.get('part'):
            title += ' - ' + str(page.get('part'))
        title = safeFileName(title) or ('BV' + re.sub(r'\W', '', bvId))

        global jm_video_title
        jm_video_title = title

        # 3. 取播放地址（这里会做 WBI 签名）
        playData, error = wbi.getPlayUrl(session, info.get('bvid') or bvId, cid)
        if error is not None:
            tk_text.insert('end', '获取播放地址失败：' + error + '\n', 'jiumeng2')
            tk_text.insert('end', '提示：如果是「账号未登录 / 请求过于频繁」，带上自己的 cookie 再试一次即可。\n')
            tk_text.see('end')
            return

        videoStream, videoError = pickVideoStream(playData)
        audioStream, audioError = pickAudioStream(playData)

        # B 站给出的 CDN 地址有效期只有几分钟，过期后再下会 403，
        # 所以下载失败时刷新一次播放地址再重试。
        playHolder = {'data': playData}

        def downloadWithRetry(picker, outPath, kind):
            stream, error = picker(playHolder['data'])
            if stream is None:
                return error
            error = downloadStream(session, streamUrls(stream), outPath,
                                   tk_text, title, kind)
            if error is None:
                return None
            tk_text.insert('end', '【{0}】{1}下载失败，正在刷新播放地址重试...\n'.format(title, kind))
            tk_text.see('end')
            newData, refreshError = wbi.getPlayUrl(session, info.get('bvid') or bvId, cid)
            if refreshError is not None:
                return error
            playHolder['data'] = newData
            stream, _ = picker(newData)
            if stream is None:
                return error
            return downloadStream(session, streamUrls(stream), outPath,
                                  tk_text, title, kind)

        if isOnlyAudio:
            if audioStream is None:
                tk_text.insert('end', '没有取到音频流：' + str(audioError) + '\n', 'jiumeng2')
                tk_text.see('end')
                return
        elif videoStream is None:
            tk_text.insert('end', '没有取到视频流：' + str(videoError) + '\n', 'jiumeng2')
            tk_text.see('end')
            return
        elif audioStream is None:
            tk_text.insert('end', '没有取到音频流：' + str(audioError) + '\n', 'jiumeng2')
            tk_text.see('end')
            return

        if isOnlyAudio:
            tk_text.insert(
                'end',
                '即将下载【{0}】的音频，音质：{1}\n'.format(
                    title, describeAudioQuality(audioStream.get('id', 0))),
                'nice')
        else:
            tk_text.insert(
                'end',
                '即将下载【{0}】:最高画质(与账号有关)：{1}，音质：{2}\n'.format(
                    title, describeQuality(videoStream.get('id', 0)),
                    describeAudioQuality(audioStream.get('id', 0) if audioStream else 0)),
                'nice')
        tk_text.see('end')

        if isOnlyAudio:
            # 只要音频时没必要把视频流也拖下来，省流量省时间
            audioPath = os.path.join(path, title + '.audio.m4s')
            tk_text.insert('end', '正在下载【' + title + '】音频....\n')
            tk_text.see('end')
            error = downloadWithRetry(pickAudioStream, audioPath, '音频')
            if error is not None:
                tk_text.insert('end', '音频下载失败：' + error + '\n', 'jiumeng2')
                tk_text.see('end')
                return
            tk_text.insert('end', '下载【' + title + '】音频完毕，开始转 MP3！\n', 'zhl')
            tk_text.see('end')
            try:
                voAuOp.extractAudio(audioPath, os.path.join(path, title + '.mp3'))
            except Exception as error:
                tk_text.insert('end', '转 MP3 失败：' + str(error) + '\n', 'jiumeng2')
                tk_text.see('end')
                return
            if os.path.exists(audioPath):
                os.remove(audioPath)
            tk_text.insert(
                'end',
                '【' + title + '】音频已成功输出到指定目录中!!!!!!!!!!!!!!!！\n----------\n',
                'jiumeng2')
            tk_text.see('end')
            return

        # 4. 音视频分别下载（多线程）
        videoPath = os.path.join(path, title + '.video.m4s')
        audioPath = os.path.join(path, title + '.audio.m4s')
        errorHolder = {}

        def inputVideo():
            errorHolder['video'] = downloadWithRetry(pickVideoStream, videoPath, '视频')

        def inputAudio():
            errorHolder['audio'] = downloadWithRetry(pickAudioStream, audioPath, '音频')

        jm_Thread1_1 = threading.Thread(target=inputAudio)
        jm_Thread1_2 = threading.Thread(target=inputVideo)
        jm_Thread1_1.start()
        jm_Thread1_2.start()
        jm_Thread1_1.join()
        jm_Thread1_2.join()  # 等待两个下载线程结束再合成，防止文件没写完就合并

        if errorHolder.get('video') or errorHolder.get('audio'):
            tk_text.insert(
                'end',
                '下载失败：视频流 {0} / 音频流 {1}\n'.format(
                    errorHolder.get('video'), errorHolder.get('audio')),
                'jiumeng2')
            tk_text.see('end')
            return

        # 5. 合成
        tk_text.insert('end', '开始对 【' + title + '】 进行音视频合并！请耐心等候...(ffmpeg合成中)\n')
        tk_text.insert('end', '视频过长时，建议挂机等待~~~~~\n')
        tk_text.see('end')
        try:
            video_audio_merge_ffmpeg(title, path)
        except Exception as error:
            tk_text.insert('end', '音视频合并失败：' + str(error) + '\n', 'jiumeng2')
            tk_text.see('end')
            return
        tk_text.insert(
            'end',
            '【' + title + '】视频已成功整合到输出目录中!!!!!!!!!!!!!!!！\n----------\n',
            'jiumeng2')
        tk_text.see('end')

    # 不另外用一个线程的话，tkinter模块会原地打转
    jm_Thread1 = threading.Thread(target=work)
    jm_Thread1.start()
    if wait:
        jm_Thread1.join()

    return path


def downloadSync(bilibiliUrl, path, global_dict, num=1, isOnlyAudio=False):
    """
    同步版本：下载完成后才返回，命令行 / 脚本里用它比较省心。
    :param bilibiliUrl: 视频链接或 BV 号
    :param path: 输出目录
    :param global_dict: 含 'text' 的字典，文本性对象只要有 insert/see/tag_config 即可
    :param num: 分P（链接里带 ?p=xx 时以链接为准）
    :param isOnlyAudio: True 时只输出 mp3
    :return: 输出目录
    """
    parsed = parseVideoUrl(bilibiliUrl)
    page = parsed['p'] or int(num)
    bvId = parsed['bvid'] or ('av' + parsed['aid'])
    return getVideoByBV(bvId, path, global_dict,
                        isOnlyAudio=isOnlyAudio, pageNum=page, wait=True)


def main(bilibiliUrl, path, global_dict, num):
    """
    向外暴露使用方法，通过对应的url下载视频。
    :param bilibiliUrl: 哔哩哔哩视频URL
    :param path: 路径
    :param global_dict : 用于传输tkinter文本输出框对象，便于在此模块写一些信息到输出框
    :param num : 视频集数
    :return:
    """
    _startDownload(bilibiliUrl, path, global_dict, num, isOnlyAudio=False)


def main_onlyAudio(bilibiliUrl, path, global_dict, num):
    """
    向外暴露使用方法，只下载音频并转成 MP3。
    :param bilibiliUrl: 哔哩哔哩视频URL
    :param path: 路径
    :param global_dict : 用于传输tkinter文本输出框对象，便于在此模块写一些信息到输出框
    :param num : 视频集数
    :return:
    """
    _startDownload(bilibiliUrl, path, global_dict, num, isOnlyAudio=True)


def _startDownload(bilibiliUrl, path, global_dict, num, isOnlyAudio=False):
    """
    解析链接这一步可能会联网（短链展开），所以放到线程里做，避免界面卡住。
    链接里的 ?p=xx 优先于界面上填的集数。
    """
    def parseAndRun():
        try:
            parsed = parseVideoUrl(bilibiliUrl)
            page = parsed['p'] or int(num)
            bvId = parsed['bvid'] or ('av' + parsed['aid'])
        except Exception as error:
            tk_text = global_dict.get('text')
            if tk_text is not None:
                tk_text.tag_config('jiumeng2', foreground='red')
                tk_text.insert('end', str(error) + '\n', 'jiumeng2')
                tk_text.see('end')
            return
        getVideoByBV(bvId, path, global_dict, isOnlyAudio=isOnlyAudio, pageNum=page)

    threading.Thread(target=parseAndRun).start()

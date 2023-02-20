"""
用于处理下载视频模块的信息。
"""

import requests
import re  # 正则表达式
import json
import os
# from moviepy.editor import *  # 处理音频和视频合成，如果用video_audio_merge_moviepy方法，则需要引入该模块
import threading
import ffmpeg  # 处理音频和视频合成
from getVideoPicture import getDefaultFileNameByHtmlData  # 获取用户名+视频标题。


# 伪造请求头,携带cookie，以获取更高画质的video
headers = {
    'Connection': 'Keep-Alive',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'referer': 'https://www.bilibili.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',

}


# https://www.bilibili.com/video/BV1124y117Dr/?p=9&spm_id_from=333.1007.top_right_bar_window_history.content.click&vd_source=88de6d7bf2afd93889536491926ffed3
def getBVbyUrl(urlStr):  # 通过url字符串拆分出对应的BV号。
    result = re.search(r'[AB]V([\w\W]*)[/?]', urlStr).group()  # 用 group 提取正则表达式结果，([\w\W]*)表示所有差异
    result = result.replace('/', '')
    result = result.replace('?', '')
    return result


# 获取响应内容
def get_page(url):
    """
    用来处理url的请求发送，获取response
    :param url:
    :return: 正常返回处理后的response。
    """
    try:
        cookieFile = open('info.json', 'r')
        headers_cookie = json.load(cookieFile)['cookie']
        cookieFile.close()
        # request 模块有坑，反正B站的cookie信息一定要放在cookies里面
        s = requests.Session().get(url, headers=headers, cookies=headers_cookie)
        s.raise_for_status()  # 用来判断返回的状态码是不是200，不是将抛出异常。
        s.encoding = s.apparent_encoding  # 用来从内容分析出的响应内容编码方式，处理乱码
        return s
    except:
        return '解析网页失败，请检查！'


# 拆解返回的结果，解析出对应的音视频URL和 标题
def parse_page(data):
    """
    data 为 获取请求返回的response转text后的内容。
    :param data:
    :return:
    """
    # re.s 参数 ：使用该参数后，正则表达式会将整个字符串作为一个整体，将'\n"当做一个普通字符来匹配，
    # 也就是类似 js的 /略/s，原来Python是这样用关键词语的（贪婪模式)
    json_str = re.findall('<script>window.__playinfo__=(.*?)</script>', data, re.S)[0]

    json_data = json.loads(json_str)  # 将str转换为字典类型
    # -----------------
    file = open('about.json', 'w')
    jm_new = {'info': json_data}
    json.dump(jm_new, file)
    file.close()
    # -----------------
    down_list = []
    # title = re.findall('name="title" content="(.*?)">', data, re.S)[0]
    # title = title.replace('_哔哩哔哩_bilibili', '')  # B站视频新后缀，进行过滤。
    title = getDefaultFileNameByHtmlData(data)
    # 获取到音频 和 视频的 实际url地址。
    audio_url = json_data['data']['dash']['audio'][0]['backup_url'][-1]
    video_url = json_data['data']['dash']['video'][0]['backup_url'][-1]
    down_list.append(audio_url)
    down_list.append(video_url)
    down_list.append(title)

    # 添加画质值。
    pictureQualityInfo = json_data['data']['dash']['video'][0]['id']
    pictureQuality = ''
    if pictureQualityInfo == 120:
        pictureQuality = '4K 超清 '
    elif 120 > pictureQualityInfo > 80:
        pictureQuality = '1080P 高码率'
    elif pictureQualityInfo == 80:
        pictureQuality = '1080P 高清'
    elif pictureQualityInfo == 64:
        pictureQuality = '720P 高清'
    elif pictureQualityInfo == 32:
        pictureQuality = '480P 清晰'
    elif pictureQualityInfo == 16:
        pictureQuality = '360P 流畅'
    else:
        pictureQuality = '未知画质,画质质量值：'+ str(pictureQualityInfo)
    down_list.append(pictureQuality)

    # 测试研究部分
    # 研究爬取的过程中，发现，我们的传入的cookie对应的账号没有开会员，则接收的url本身就没有会员级别的，因此不用处理了。
    # 但是反过来猜测，如果有菩萨提供大会员的 SESSDATA 的值 ，则可以实现下载超清画质，可惜不想充钱给B站，因此无法实践。
    # jm_test_video = json_data['data']['dash']['video']
    # for i in jm_test_video:  # 查看最高id是否超过80，超过则是会员画质
    #     print('---------------------')
    #     print(i)
    #     print(i['id'])
    #     print('-------------------')

    return down_list  # 返回带有原视频 音频url 和 标题信息的 列表


# 写入视频文件
def write_res(filename, data, path):
    """
    写入信息到对应文件夹。
    :param filename: 文件名称
    :param data: 数据
    :param path: 文件路径
    :return:
    """
    with open(r''+path + '/' + filename, 'wb') as f:
        f.write(data)
        f.close()


# 合并音视频之moviepy模块，已放弃。
# def video_audio_merge_moviepy(video_name, filePath):
#     """
#     合并音频和视频。并且将原先的单独的音频和视频做删除处理。
#     moviepy 模块处理音视频合成是在太慢啦，已放弃
#     :param video_name: 视频名称
#     :param filePath : 指定的路径
#     :return:
#     """
#     myAudioName = video_name + '.mp3'
#     myVideoName = video_name + '.mp4'
#     myAudioPath = filePath + '/' + myAudioName
#     myVideoPath = filePath + '/' + myVideoName
#     # 提取音频
#     audio = AudioFileClip(myAudioPath)
#     # 读入视频
#     video = VideoFileClip(myVideoPath)
#     # 将音轨合并到 视频中
#     video = video.set_audio(audio)
#     # 输出到指定路径,最慢的步骤
#     video.write_videofile(f"{filePath+'/'+video_name}_jm.mp4", threads=8)

def ff():
    print(1)


# 音视频合成之 FFmpeg
def video_audio_merge_ffmpeg(video_name, filePath):
    """
    合并音频和视频，相比moviepy，ffmpeg 快极了！
    我们本地下载好 ffmpeg.exe 然后复制到项目中，就可以用了
    :param video_name: 视频名称
    :param filePath: 指定的输出路径
    :return:
    """
    myAudioName = video_name + '.mp3'
    myVideoName = video_name + '.mp4'
    myAudioPath = filePath + '/' + myAudioName  # 需要合成的音频路径
    myVideoPath = filePath + '/' + myVideoName  # 需要合成的视频路径
    output_path = filePath + '/' + video_name + '_jm.mp4'   # 合成的视频输出路径
    audio_file = ffmpeg.input(myAudioPath)
    video_file = ffmpeg.input(myVideoPath)
    # output_file = ffmpeg.output(audio_file, video_file, filename=output_path,
    #                             vcodec='copy', acodec='aac', strict='experimental', pix_fmt='yuv420p')
    # process = output_file.overwrite_output()
    #
    # ffmpeg_path = 'ffmpeg.exe'
    # process.run_async(cmd=ffmpeg_path, pipe_stdin=True, pipe_stdout=False, pipe_stderr=False)
    # 上面几行的注释无法获知何时合成完毕，会影响我们删除原音频和原视频的操作，导致报错。
    ffmpeg.output(audio_file, video_file, output_path).run()
    print('音视频合成结束')
    # 删除分离前的视频和音频
    os.remove(filePath + '/' + video_name + '.mp4')
    os.remove(filePath + '/' + video_name + '.mp3')


# 通过BV号获取下载音视频
def getVideoByBV(bvNo, path, global_dict):  # 通过BV号获取音频和视频
    """
    用于 通过BV号爬取信息
    :param bvNo:
    :param path:
    :param global_dict: 方便输出信息到text框
    :return:
    """
    # 进行多线程处理,避免tkinter一直在转，等待。

    def getUrlList():
        tk_text = global_dict['text']  # 主输出台的text文本框
        # 配置颜色
        tk_text.tag_config('jiumeng2', foreground='red')
        tk_text.tag_config('zhl', foreground='deeppink')
        tk_text.tag_config('nice',  foreground='#281285')
        tk_text.insert('end', '获取到的BV号为:' + bvNo + '\n')
        url2 = f'http://www.bilibili.com/video/{bvNo}'
        if type(get_page(url2)) is str:
            print(get_page(url2))  # 解析网页失败
        else:
            html_data = get_page(url2).text  # 获取响应内容并且转换为 文本格式。

            # hfile = open('B站网站代码研究.html', 'w', encoding='utf-8')  #用于研究B站的网站内容结构，分析时用。
            # hfile.write(html_data)  # 将 response文本内容写入到 html中。

            down_url_list = parse_page(html_data)  # 得到带有音频和视频url的列表。

            # 获取到该音频去除了干扰信息后的标题。
            title = down_url_list[2].replace(' ', '').replace('_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili', '')
            pictureQuality = down_url_list[-1]

            tk_text.insert('end', f'即将下载本视频【{title}】:最高画质(与账号有关)：' + pictureQuality + '\n', 'nice')

            # 获取请求响应的内容
            def inputAudio():
                # sava audio
                audio_url = down_url_list[0]  # 信息字典的第一个元素是 音频url。
                audio_content = get_page(url=audio_url).content
                tk_text.insert('end', '正在下载【' + title + '】音频....\n')
                write_res(filename=title + '.mp3', data=audio_content, path=path)
                print('保存音频成功！')
                tk_text.insert('end', '下载【' + title + '】音频完毕！\n', 'zhl')

            def inputVideo():
                # save video
                video_url = down_url_list[1]
                video_content = get_page(url=video_url).content
                tk_text.insert('end', '正在下载【' + title + '】视频....\n')
                write_res(filename=title + '.mp4', data=video_content, path=path)
                print('保存视频成功！')
                tk_text.insert('end', '下载【' + title + '】视频完毕！\n', 'zhl')

            jm_Thread1_1 = threading.Thread(target=inputAudio)
            jm_Thread1_2 = threading.Thread(target=inputVideo)
            jm_Thread1_1.start()
            jm_Thread1_2.start()
            jm_Thread1_1.join()
            jm_Thread1_2.join()  # 用处是下面的代码会等待join完毕再执行,防止还没下载完就合并，线程出错

            # 接下来进行音频和视频的整合。
            tk_text.insert('end', '开始对 【' + title + '】 进行音视频合并！请耐心等候...(ffmpeg合成中)\n')
            tk_text.insert('end', '视频过长时，建议挂机等待~~~~~\n')
            # jm_Thread1_3 = threading.Thread(target=video_audio_merge_ffmpeg, args=(title, path))
            # jm_Thread1_3.start()
            # jm_Thread1_3.join()
            video_audio_merge_ffmpeg(title, path)
            tk_text.insert('end', '【' + title + '】视频已成功整合到输出目录中!!!!!!!!!!!!!!!！\n----------\n', 'jiumeng2')

    # 不另外用一个线程的话，tkinter模块会原地打转
    jm_Thread1 = threading.Thread(target=getUrlList)
    jm_Thread1.start()


def main(bilibiliUrl, path, global_dict, num):
    """
    向外暴露使用方法，通过对应的url下载视频。
    :param bilibiliUrl: 哔哩哔哩视频URL
    :param path: 路径
    :param global_dict : 用于传输tkinter文本输出框对象，便于在此模块写一些信息到输出框
    :param num : 视频集数
    :return:
    """
    if num != 1:
        BV = getBVbyUrl(bilibiliUrl)+'?p='+str(num)
    else:
        BV = getBVbyUrl(bilibiliUrl)
    getVideoByBV(BV, path, global_dict)



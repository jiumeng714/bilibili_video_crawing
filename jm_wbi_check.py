"""
WBI 自检 / 排查脚本：怀疑「取不到播放地址、画质偏低、被风控」时先跑它。

用法（项目根目录执行）：
    python jm_wbi_check.py BV1B8rPBCELm
    python jm_wbi_check.py "https://www.bilibili.com/video/BV1B8rPBCELm/"
"""

import sys

import getVideo as gv
import wbi


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else 'BV1B8rPBCELm'
    parsed = gv.parseVideoUrl(arg)
    bvId = parsed['bvid'] or ('av' + parsed['aid'])
    isAv = bvId.lower().startswith('av')

    session = wbi.createSession(gv.loadCookie())
    print('会话里的 cookie 字段：', sorted(session.cookies.get_dict().keys()))

    mixinKey, error = wbi.getWbiKeys(session)
    print('mixin_key：', mixinKey, '| 错误：', error)

    info, error = wbi.getVideoInfo(
        session, aid=bvId[2:] if isAv else None, bvid=None if isAv else bvId)
    print('view 接口错误：', error)
    if error:
        return 1

    print('标题：', info['title'])
    print('UP主：', info['owner']['name'])
    print('封面：', info['pic'])
    print('分P数：', len(info.get('pages') or []))

    cid = (info.get('pages') or [{}])[0].get('cid') or info['cid']
    playData, error = wbi.getPlayUrl(session, info['bvid'], cid)
    print('playurl 接口错误：', error)
    if error:
        return 1

    print('该稿件支持的画质：', playData.get('accept_description'))
    video, videoError = gv.pickVideoStream(playData)
    audio, audioError = gv.pickAudioStream(playData)
    if video:
        print('当前账号实际能拿到：{0}（id={1}，{2}x{3}）'.format(
            gv.describeQuality(video['id']), video['id'],
            video['width'], video['height']))
    else:
        print('视频流：', videoError)
    if audio:
        print('音频：{0}（id={1}）'.format(
            gv.describeAudioQuality(audio['id']), audio['id']))
    else:
        print('音频流：', audioError)
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""
用来获取B站视频封面，质量为原图。

2026 修订说明：封面地址、UP主、标题以前是靠正则去网页的 itemprop 标签里抠，
页面结构一变就全废。现在统一走官方 view 接口拿 pic / owner / title。
"""

import os

import requests

import wbi  # WBI 签名与官方 API 封装
from jmCommon import loadCookie, safeFileName  # 公共小工具


def getVideoInfoByBv(bvNo):
    """
    拿视频基本信息。
    :return: (info_dict, error_msg)
    """
    session = wbi.createSession(loadCookie())
    bvId = str(bvNo).strip()
    if bvId.lower().startswith('av'):
        return wbi.getVideoInfo(session, aid=bvId[2:])
    return wbi.getVideoInfo(session, bvid=bvId)


def getDefaultFileName(bvNo):
    """
    生成默认文件名：[UP主] - 标题
    """
    info, error = getVideoInfoByBv(bvNo)
    if error is not None or not info:
        return '旧梦'
    title = '[{0}] - {1}'.format(
        info.get('owner', {}).get('name', 'unknown'), info.get('title', ''))
    return safeFileName(title) or '旧梦'


def getPictureUrl(bvNo):
    """
    获取封面原图地址（接口返回的 pic 本身就是原图，@ 后缀是缩略参数，这里不带）。
    """
    info, error = getVideoInfoByBv(bvNo)
    if error is None and info and info.get('pic'):
        return info['pic'].replace('http://', 'https://', 1)
    # 失败时：返回我的百度头像地址
    return '//himg.bdimg.com/sys/portraitn/item/public.1.a8f88370.dMVW5WwBuH51v92oqmRXJw'


def getPictureMain(bvNo, global_dict, fileName):
    """
    下载封面原图。
    :param bvNo: BV 号
    :param global_dict: 主界面 text 文本框
    :param fileName: 用户选定的保存路径（不带后缀时自动补上图片自身的后缀）
    :return: 保存后的完整路径，失败返回 None
    """
    tk_text = global_dict.get('text')
    if tk_text is not None:
        tk_text.tag_config('freshGreen', foreground='#99cf15')

    info, error = getVideoInfoByBv(bvNo)
    if error is not None or not info or not info.get('pic'):
        if tk_text is not None:
            tk_text.insert('end', '获取封面地址失败：{0}\n'.format(error), 'freshGreen')
            tk_text.see('end')
        return None

    pictureUrl = info['pic'].replace('http://', 'https://', 1)
    if tk_text is not None:
        tk_text.insert('end', '图片地址：(也可浏览器访问)\n' + pictureUrl + '\n', 'freshGreen')
        tk_text.see('end')

    response = requests.get(pictureUrl, headers=wbi.DEFAULT_HEADERS, timeout=30)
    response.raise_for_status()

    # 用户没写后缀时，按图片自身的格式补一个
    suffix = os.path.splitext(fileName)[1]
    if suffix == '':
        urlSuffix = os.path.splitext(pictureUrl.split('?')[0])[1] or '.jpg'
        pictureName = fileName + urlSuffix
    else:
        pictureName = fileName

    with open(pictureName, 'wb') as fileObj:
        fileObj.write(response.content)
    if tk_text is not None:
        tk_text.insert('end', '保存图片成功！' + pictureName + '\n', 'freshGreen')
        tk_text.see('end')
    return pictureName

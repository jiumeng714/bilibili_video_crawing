"""
B站 WBI 签名与官方 API 请求封装。

2023 年之后 B 站把 WBI 签名变成了强制项：
1. 从 nav 接口拿到 img_key / sub_key（其实就是 wbi 图片文件名的 32 位 MD5）；
2. 把两个 key 拼起来，按照固定的混淆表重排，取前 32 位得到 mixin_key；
3. 把请求参数按 key 的字典序排序，拼上时间戳 wts 与 mixin_key，做 MD5 得到 w_rid。

本模块把这些逻辑以及「浏览器同款请求头 / buvid 指纹 / 会话管理」都收拢在一起，
供 getVideo.py、getVideoPicture.py 等模块调用。
"""

import hashlib
import time
import urllib.parse

import requests

# 请求头：B 站对 UA、Referer 校验很严，缺失时接口会返回 -352 风控或者 CDN 返回 403
DEFAULT_HEADERS = {
    'Connection': 'keep-alive',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': '*/*',
    'Origin': 'https://www.bilibili.com',
    'referer': 'https://www.bilibili.com/',
    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
}

# 接口地址
API_NAV = 'https://api.bilibili.com/x/web-interface/nav'
API_SPI = 'https://api.bilibili.com/x/frontend/finger/spi'
API_VIEW = 'https://api.bilibili.com/x/web-interface/view'
API_PLAYURL = 'https://api.bilibili.com/x/player/wbi/playurl'

# WBI 混淆表（bilibili-API-collect 中公布的固定值）
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]

# 缓存 wbi 密钥，避免每次请求都去问一次 nav 接口
_wbi_keys_cache = {'mixin_key': None, 'expire_at': 0}
_WBI_KEYS_TTL = 60 * 30  # 30 分钟


def getMixinKey(img_key, sub_key):
    """
    将 img_key 与 sub_key 拼接后按混淆表重排，取前 32 位得到 mixin_key。
    :param img_key: nav 接口返回的 img_url 的文件名（不带后缀）
    :param sub_key: nav 接口返回的 sub_url 的文件名（不带后缀）
    :return: 32 位的 mixin_key
    """
    orig = str(img_key) + str(sub_key)
    return ''.join(orig[i] for i in MIXIN_KEY_ENC_TAB if i < len(orig))[:32]


def encWbi(params, mixin_key, wts=None):
    """
    对参数做 WBI 签名，返回可以直接拼在 url 后面的查询字符串（已带 w_rid 与 wts）。
    :param params: dict，业务参数
    :param mixin_key: getMixinKey 得到的混入密钥
    :param wts: 时间戳，默认取当前时间
    :return: 形如 `a=1&b=2&wts=1700000000&w_rid=xxxxxxxx` 的字符串
    """
    new_params = dict(params)
    new_params['wts'] = str(int(time.time()) if wts is None else int(wts))
    # B 站规定：参数值里不允许出现 ! ' ( ) * 这五个字符，先过滤掉
    new_params = {
        key: ''.join(ch for ch in str(value) if ch not in "!'()*")
        for key, value in new_params.items()
    }
    # 按 key 的字典序排序后拼接（urlencode 会把空格变成 +，与 B 站前端行为一致）
    query = urllib.parse.urlencode(sorted(new_params.items()))
    w_rid = hashlib.md5((query + mixin_key).encode('utf-8')).hexdigest()
    return query + '&w_rid=' + w_rid


def getPageJson(session, url, params=None, timeout=15, retry=3, acceptCodes=()):
    """
    发送 GET 请求并解析 JSON，失败（网络异常 / 风控）时自动重试。
    :param acceptCodes: 允许的非 0 code，例如 nav 接口未登录时返回 -101 但依然带着 wbi 密钥
    :return: (json_dict, error_msg)，取到数据时 error_msg 为 None
    """
    last_error = ''
    for _ in range(max(1, retry)):
        try:
            response = session.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)
            response.raise_for_status()
            result = response.json()
        except Exception as error:  # 网络异常、非 JSON 响应等
            last_error = '请求 {} 失败：{}'.format(url, error)
            continue
        if result.get('code') == 0 or result.get('code') in acceptCodes:
            return result, None
        last_error = '接口返回错误 code={} message={}'.format(
            result.get('code'), result.get('message'))
        # -352 是风控，稍等一下再试说不定就过了
        if result.get('code') != -352:
            break
        time.sleep(1)
    return None, last_error


def getWbiKeys(session, force=False):
    """
    从 nav 接口获取 img_key / sub_key 并组装出 mixin_key（带缓存）。
    :return: (mixin_key, error_msg)
    """
    now = time.time()
    if not force and _wbi_keys_cache['mixin_key'] and _wbi_keys_cache['expire_at'] > now:
        return _wbi_keys_cache['mixin_key'], None

    # 未登录时 nav 接口返回 code=-101，但 wbi_img 字段照样是有效的，所以这里放行
    result, error = getPageJson(session, API_NAV, acceptCodes=(-101,))
    if error is not None:
        return None, error

    wbi_img = result.get('data', {}).get('wbi_img', {})
    img_url = wbi_img.get('img_url', '')
    sub_url = wbi_img.get('sub_url', '')
    if not img_url or not sub_url:
        return None, 'nav 接口没有返回 wbi 密钥，请稍后再试'

    img_key = img_url.rsplit('/', 1)[-1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[-1].split('.')[0]
    mixin_key = getMixinKey(img_key, sub_key)
    _wbi_keys_cache['mixin_key'] = mixin_key
    _wbi_keys_cache['expire_at'] = now + _WBI_KEYS_TTL
    return mixin_key, None


def createSession(cookie_dict=None):
    """
    创建一个带浏览器请求头、buvid 指纹与用户 cookie 的会话对象。
    :param cookie_dict: 从 info.json 中读出的 cookie 字典，可为 None
    :return: requests.Session
    """
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    if cookie_dict:
        session.cookies.update(cookie_dict)
    if 'buvid3' not in session.cookies:
        # 没有 buvid 时容易触发风控，先向 spi 接口要一个匿名指纹
        try:
            response = session.get(API_SPI, headers=DEFAULT_HEADERS, timeout=10)
            data = response.json().get('data', {})
            if data.get('b_3'):
                session.cookies.set('buvid3', data['b_3'], domain='.bilibili.com')
            if data.get('b_4'):
                session.cookies.set('buvid4', data['b_4'], domain='.bilibili.com')
        except Exception:
            pass  # 拿不到也不影响主流程，只是更容易触发风控
    return session


def getVideoInfo(session, bvid=None, aid=None):
    """
    调用 view 接口获取视频基本信息（标题、UP主、封面、cid 列表）。
    :return: (info_dict, error_msg)
    """
    params = {'bvid': bvid} if bvid else {'aid': str(aid).lstrip('avAV')}
    result, error = getPageJson(session, API_VIEW, params=params)
    if error is not None:
        return None, '获取视频信息失败：' + error
    return result.get('data', {}), None


def getPlayUrl(session, bvid, cid, qn=127, fnval=4048, fourk=1):
    """
    调用 playurl(wbi) 接口获取音视频流地址，请求会自动完成 WBI 签名。
    :param qn: 请求的画质，127 表示「尽量高」
    :param fnval: 4048 表示要 dash 格式（含 HDR、4K、杜比等）
    :return: (play_data, error_msg)
    """
    mixin_key, error = getWbiKeys(session)
    if error is not None:
        return None, error

    params = {
        'bvid': bvid,
        'cid': cid,
        'qn': qn,
        'fnver': 0,
        'fnval': fnval,
        'fourk': fourk,
    }
    url = API_PLAYURL + '?' + encWbi(params, mixin_key)
    result, error = getPageJson(session, url)
    if error is not None:
        # 密钥可能过期了，强制刷新后再试一次
        mixin_key, error = getWbiKeys(session, force=True)
        if error is not None:
            return None, error
        url = API_PLAYURL + '?' + encWbi(params, mixin_key)
        result, error = getPageJson(session, url)
        if error is not None:
            return None, error
    return result.get('data', {}), None


if __name__ == '__main__':
    # 简单自测：打印 mixin_key 与指定视频的可用画质
    _session = createSession()
    _mixin_key, _error = getWbiKeys(_session)
    print('mixin_key =', _mixin_key, _error)
    _info, _error = getVideoInfo(_session, bvid='BV1B8rPBCELm')
    print('title =', (_info or {}).get('title'), _error)

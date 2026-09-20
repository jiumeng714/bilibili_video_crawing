"""
将Cookie字符串转成字典。

旧版本只保留 SESSDATA，其实 buvid3 / bili_jct / buvid4 这些字段一起带上更不容易被风控，
所以这里改成把整串 cookie 里的有效键值对都解析出来。
"""

# cookie 里这些是属性而不是键值对，遇到就跳过
_COOKIE_ATTRS = {
    'expires', 'max-age', 'path', 'domain', 'secure', 'httponly',
    'samesite', 'comment', 'version',
}


def getCookieDict(cookie_str):
    """
    把浏览器里复制出来的 cookie 字符串（或者 F12 里看到的 Request Headers 中的 cookie）转成字典。
    :param cookie_str: 形如 'SESSDATA=xxx; buvid3=yyy; bili_jct=zzz'
    :return: dict
    """
    cookie_str = str(cookie_str).replace('\n', '').replace('\r', '')
    result = {}
    for item in cookie_str.split(';'):
        if '=' not in item:
            continue
        name, value = item.split('=', 1)
        name = name.strip()
        value = value.strip().strip('"')
        if name == '' or name.lower() in _COOKIE_ATTRS:
            continue
        result[name] = value
    return result


def getCookieNewStr(cookie_str):
    """
    把 cookie 字符串规范化成 'k=v; k2=v2' 的形式。
    """
    cookieDict = getCookieDict(cookie_str)
    return '; '.join('{0}={1}'.format(name, value) for name, value in cookieDict.items())


def getSessData(cookie_str):
    """
    只取 SESSDATA（有些老代码只需要这一个字段）。
    :return: SESSDATA 的值，没有则返回 None
    """
    cookieDict = getCookieDict(cookie_str)
    return cookieDict.get('SESSDATA')

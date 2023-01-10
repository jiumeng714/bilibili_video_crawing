"""
将Cookie字符串转成字典
"""
import re


def getCookieDict(cookie_str):
    # file = open('info.json','r')
    # result = json.load(file)
    # cookie_str = result['cookie']
    cookie_str = cookie_str.replace('\n', '')
    # 下面将过滤 cookie字符串，找出里面的 核心 SESSDATA
    result = re.search('SESSDATA([\w\W])*;', cookie_str).group()  # 由于是贪婪模式，还要过滤
    new_cookie_dict = result.split(';')[0]   # 确保只保留 SESSDATA
    # 转字典
    sessionData = new_cookie_dict.split('=')
    cookie_name = sessionData[0]
    cookie_value = sessionData[1]

    return {str(cookie_name): cookie_value}


def getCookieNewStr(cookie_str):
    # file = open('info.json','r')
    # result = json.load(file)
    # cookie_str = result['cookie']
    cookie_str = cookie_str.replace('\n', '')
    # 下面进行将字符串转字典操作
    cookie_str_list = str.split(cookie_str, ';')
    new_cookie = ''
    for param in cookie_str_list:
        params = str.split(param, '=')
        name = params[0].strip()
        value = params[1].strip()
        new_cookie += name + '=' + value + '; '
    new_cookie = new_cookie.rstrip(';')
    return new_cookie

"""
几个公共小工具：读取 cookie、把标题洗成合法文件名。
单独放一个模块，避免 getVideo / getVideoPicture 之间互相 import。
"""

import json
import re


def loadCookie():
    """
    从 info.json 读出 cookie 字典，过滤掉占位 / 空值。
    :return: dict
    """
    placeholder = {'', '12345678', 'SESSDATA'}
    try:
        with open('info.json', 'r', encoding='utf-8') as cookieFile:
            cookie = json.load(cookieFile).get('cookie') or {}
    except Exception:
        return {}
    return {name: value for name, value in cookie.items() if value not in placeholder}


def safeFileName(name):
    """
    过滤掉文件名里不能用的特殊字符（沿用原项目的白名单规则）。
    """
    keep = re.compile(r"[^\u4e00-\u9fa5a-zA-Z0-9,，：:._~【】\-\[\]（）()＋+ ]")
    return keep.sub('', str(name)).strip()

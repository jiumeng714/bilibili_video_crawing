"""
用来获取B站视频封面，质量为原图
"""
import re
import requests

# 伪造请求头,无需携带Cookie了，只是获取个图片
headers = {
    'Connection': 'Keep-Alive',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'referer': 'https://www.bilibili.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
}


# 获取响应内容
def get_page_info(url):
    """
    用来处理url的请求发送，获取response
    :param url:
    :return: 正常返回处理后的response。
    """
    try:
        s = requests.Session().get(url, headers=headers)
        s.raise_for_status()  # 用来判断返回的状态码是不是200，不是将抛出异常。
        s.encoding = s.apparent_encoding  # 用来从内容分析出的响应内容编码方式，处理乱码
        return s
    except:
        return '解析网页失败，请检查!'


# 给视频模块调用的
def getDefaultFileNameByHtmlData(html_data):
    title = re.findall('name="title" content="(.*?)">', html_data, re.S)[0]  # 视频标题
    # 对标题做规则化处理，过滤预定外的特殊字符防止输出文件报错
    res = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9^,^_^，^：^:^.^~^【^】^\-^-^\[^\]]")
    title = res.sub('', title)  # 过滤特殊字符,只保留中文和一些数字，英文，日常使用字符。
    title = title.replace('_哔哩哔哩_bilibili', '')

    # 上面是标题，下面获取up主名字
    json_str = re.findall('itemprop="author(.*?)>', html_data, re.S)[0]
    content = re.search('content="(.*)"', json_str, re.S).group()
    content = content.replace('content="', '')
    content = content.replace('"', '')

    title = '['+content + '] - ' + title

    return title


def getDefaultFileName(bvNo):
    url2 = f'http://www.bilibili.com/video/{bvNo}'
    result = get_page_info(url2)
    if type(result) != str:
        html_data = result.text
        title = getDefaultFileNameByHtmlData(html_data)
        return title
    return '旧梦'


# 总函数
def getPictureMain(bvNo, global_dict, fileName):
    url2 = f'http://www.bilibili.com/video/{bvNo}'
    result = get_page_info(url2)
    tk_text = global_dict['text']  # 主输出台的text文本框
    tk_text.tag_config('freshGreen',  foreground='#99cf15')
    if type(result) != str:
        html_data = result.text

        # 经过研究，封面的url就在itemprop="image里面的content的值中。@后面是略缩图了，不需要。
        json_str = re.findall('itemprop="image(.*?)>', html_data, re.S)[0]
        new_str = re.search('content=(.*)@', json_str, re.S).group()
        # 修剪
        new_str = new_str.lstrip("content=")
        new_str = new_str.lstrip("'")
        new_str = new_str.lstrip('"')
        new_str = new_str.rstrip('@')
        final_picture_url = 'https:'+new_str  # 成功获取到图片地址
        tk_text.insert('end', '图片地址：(也可浏览器访问)\n'+new_str+'\n', 'freshGreen')
        # 接下来下载图片。
        postfix = new_str.split('.')[-1]
        pictureName = fileName + '.' + postfix  # 要输出的文件名称
        res = requests.get(final_picture_url)
        with open(pictureName, 'wb') as file_obj:
            file_obj.write(res.content)
            file_obj.close()
        tk_text.insert('end', '保存图片成功！' + pictureName + '\n', 'freshGreen')

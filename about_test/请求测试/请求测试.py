import json
import requests
import re

# headers_cookie = "SESSDATA='d157dd5f,1677676302,81dd2*91'"
headers_cookie = "SESSDATA=d157dd5f,1677676302,81dd2*91"
headers = {
    'Connection': 'Keep-Alive',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'referer': 'https://www.bilibili.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
    'Cookie': "SESSDATA=d157dd5f,1677676302,81dd2*91;"
}

# 获取响应内容
def get_page(url):
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
        return '解析网页失败，请检查！'

def main(  num):
    """
    向外暴露使用方法，通过对应的url下载视频。
    :param bilibiliUrl:
    :return:
    """
    if num != 1:
        BV = 'BV1wR4y1U7FP' + '?p=' + str(num)
    else:
        BV = 'getBVbyUrl'

    url2 = f'http://www.bilibili.com/video/{BV}'
    print(get_page(url2))  # 解析网页失败
    html_data = get_page(url2).text  # 获取响应内容并且转换为 文本格式。
    print(html_data)

    hfile = open('jiumeng.html', 'w', encoding='utf-8')
    hfile.write(html_data)  # 将 response文本内容写入到 html中。

    json_str = re.findall('<script>window.__playinfo__=(.*?)</script>', html_data, re.S)
    print('json',json_str)

    # # print('json_str')
    # # print(json_str)
    # json_data = json.loads(json_str)  # 将str转换为字典类型
    # # -----------------
    # file = open('about.json', 'w')
    # jm_new = {'info': json_data}
    # json.dump(jm_new, file)
    # file.close()
    # # -----------------
    # down_list = []
    # title = re.findall('name="title" content="(.*?)">', data, re.S)[0]
    # # 获取到音频 和 视频的 实际url地址。
    # audio_url = json_data['data']['dash']['audio'][0]['backup_url'][-1]
    # video_url = json_data['data']['dash']['video'][0]['backup_url'][-1]
    # down_list.append(audio_url)
    # down_list.append(video_url)
    # down_list.append(title)

if __name__ == '__main__':
    main(1)
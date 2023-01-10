import random
import os
import json
from threading import Thread
import requests
from lxml import etree


def postRequest(url):
    """对该视频进行请求"""
    res = requests.get(url=url,headers=headers)
    if res.status_code == 200:
        html = res.text
        print("请求成功！")
        return html, url


def gainVideoUrl(html):
    """实现下载bilibili视频"""

    tree = etree.HTML(html)
    # 提取获取视频相关总信息
    # datad = tree.xpath('//script[4]/text()')[0].replace('window.__playinfo__=', '')
    datad = re.findall('<script>window.__playinfo__=(.*?)</script>', data, re.S)[0]
    print(datad)
    dict2 = json.loads(datad)
    # 提取画质列表
    description = dict2['data']['accept_description']
    # 提取不同画质下的视频url
    video = dict2['data']['dash']['video']
    print('---video------')
    print(video)
    print('---video------')
    # 提取视频的音频
    audio = dict2['data']['dash']['audio']
    audio_url = audio[0]['baseUrl']

    # 将只有会员才能下载的两种画质进行剔除
    print("该视频画质有{}".format(description))
    if '超清 4K' in description:
        description.remove('超清 4K')
    if '高清 1080P60' in description:
        description.remove('高清 1080P60')

    # 创建视频画质对应id的字典
    descriptionDict = {}
    for i in description:
        if i == '流畅 360P':
            descriptionDict['流畅 360P'] = 16
        if i == '清晰 480P':
            descriptionDict['清晰 480P'] = 32
        if i == '高清 720P':
            descriptionDict['高清 720P'] = 64
        if i == '高清 1080P':
            descriptionDict['高清 1080P'] = 80
        '''4K超清的因为我没开会员，所以并不知道其相应的id'''

    id = input("可选择下载的视频画质{}\n输入相应视频画质后的数字即可：".format(descriptionDict))
    for vu in video:
        if vu['id'] == int(id):
            select_url = vu['baseUrl']

            return select_url,audio_url


def downloadVideo(video_url,title):
    """下载视频"""

    print("正在下载：{}.mp4".format(title))
    res = requests.get(url=video_url, headers=headers)

    con = res.content
    if not os.path.exists('./bilibili/'):
        os.mkdir('./bilibili/')
    with open('./bilibili/{}.mp4'.format(title), 'wb') as fp:
        fp.write(con)

    print("{}.mp4-下载完成".format(title))


def downloadAudio(audio_url,title):
    """下载音频"""

    print("正在下载：{}.mp3".format(title))
    res = requests.get(url=audio_url, headers=headers)
    con = res.content
    if not os.path.exists('./bilibili/'):
        os.mkdir('./bilibili/')
    with open('./bilibili/{}.mp3'.format(title), 'wb') as fp:
        fp.write(con)

    print("{}.mp3-下载完成".format(title))


def selecVideo(url):
    """
    单个视频与多集视频多存储实现
    """

    veri = input("当前视频为单集请输入0;多集请输入1：")
    if veri == '1':
        print("哈哈哈多线程下载视频合集我不想写了！！！惊不惊喜！！！")
        print('请自行补全合集多线程下载bilibili视频代码')

    if veri == '0':
        # 发送请求
        html, url = postRequest(url)
        # 获得视频url
        video_url, audio_url = gainVideoUrl(html)
        title = input("设置音频和视频的名称：")
        # 双线程下载视频与音频
        # vdeio_thead = Thread(target=downloadVideo, kwargs={'video_url':video_url,'title':title})
        # vdeio_thead.start()
        # audio_thead = Thread(target=downloadAudio, kwargs={'audio_url':audio_url,'title':title})
        # audio_thead.start()
        '''将两者合并即是正常视频，需要ffemg，mac弄比较麻烦，有需要的自行查文档进行自动合并'''


if __name__ == '__main__':
    # 伪造请求头
    headers = {
        'user-agent': f'Mozilla/5.0',
        'referer': 'https://www.bilibili.com/'
    }
    # 视频url网址
    url = input('请输入bilibili视频的url地址：')
    # 选择视频
    selecVideo(url)
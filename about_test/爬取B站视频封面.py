
import requests
import json
import urllib

x = 0
def get_images(url):
    headers = {'Usar-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}
    res = requests.get(url,headers=headers,timeout=(5,5))
    j = res.json()['data']
    print(j)
    # for video in res.json()['data']['list']['vlist']:
    #     global x
    #     urllib.request.urlretrieve("http:"+video['pic'],'image\%s.jpg'%x)
    #     print ("Downloading image No.{}".format(x));
    #     x += 1

for page in range(1,10):
    url = 'https://api.bilibili.com/x/space/arc/search?mid=72956117&ps=30&tid=0&pn={}&keyword=&order=pubdate&jsonp=jsonp'.format(page)
    get_images(url)
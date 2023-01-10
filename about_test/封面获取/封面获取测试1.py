import requests
url = "https://www.bilibili.com/video/BV1124y117Dr"
headers = {
    'Connection': 'Keep-Alive',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'referer': 'https://www.bilibili.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
}

res = requests.Session().get(url, headers=headers)

html_data = res.text
print(html_data)
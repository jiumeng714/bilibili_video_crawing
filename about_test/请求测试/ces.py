import requests


url = 'https://www.bilibili.com/video/BV1wR4y1U7FP/?spm_id_from=..0.0&vd_source=88de6d7bf2afd93889536491926ffed3'
head = {'cookie': "SESSDATA='d157dd5f,1677676302,81dd2*91'"}
# 先实例化一个对象
session = requests.session()
# 给 requests.session() 对象设置cookie信息，这个看情况使用，具体情况具体分析啊
cookies_dict = {}
session.cookies = requests.utils.cookiejar_from_dict(cookies_dict)
print(session.cookies)
# 后面用法和直接使用requests一样了
# get请求
response = session.get(url,cookies={'SESSDATA': 'd157dd5f,1677676302,81dd2*91'})
print(response.text)
# post请求
# response = session.post(url)
# result = response.json()
#获取登陆的所有cookies信息
# print(result.cookies.values())
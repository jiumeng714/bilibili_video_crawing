from selenium import webdriver
# 启动浏览器
browser = webdriver.Chrome()
# 打开网页，获取 Cookie
browser.get('http://www.bilibili.com')
cookie = browser.get_cookies()
# 输出 Cookie
print(cookie,type(cookie))
print(cookie[0][''])
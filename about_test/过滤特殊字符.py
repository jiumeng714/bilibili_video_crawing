import re
str = '【52kg】少女感制服穿搭🖤'
# result = re.search('([\\u4e00-\\u9fa5^a-z^A-Z^0-9]*)',str)
res = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9]")
result = res.sub('', str)
print(result)
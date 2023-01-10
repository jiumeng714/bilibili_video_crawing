import os

cmd = 'ping baidu.com'

r = os.popen(cmd)

for line in r.readlines():
    print (line)

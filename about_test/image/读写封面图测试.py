
import requests

img_src = 'https://i0.hdslb.com/bfs/archive/24fb3c34a963dc5c08c8e11f5ac0b4c422ee5bac.jpg'
response = requests.get(img_src)
with open('D:/install_video_python/1.jpg', 'wb') as file_obj:
    file_obj.write(response.content)
    print('ok')



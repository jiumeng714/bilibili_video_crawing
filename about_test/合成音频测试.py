import os
from moviepy import *
from moviepy.editor import *

# pip install moviepy
def read_filename(path):
    title1ist = []
    list1 = os.listdir(path) # os.listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表
    for i in list1:
        if "mp4" in i:
            title1ist.append(i.split(".")[0])
    return title1ist

def merge(title):
    video_path = title + '.mp4'
    audio_path = title + '.mp3'
    # 提取音轨
    audio = AudioFileClip(audio_path)
    # 读入视频
    video = VideoFileClip(video_path)
    # 将音轨合并到视频中
    video = video.set_audio(audio)
    # 输出
    video.write_videofile(f"{title}(含音频).mp4")

if __name__ == '__main__':
    path=r"D:\files\mp4"
    titlelist = read_filename(path)
    print('开始合并视频与音频')
    for title in titlelist:
        title = os.path.join(path, title)
        # print(title)
        merge(title)
    print('有音频视频处理完成')

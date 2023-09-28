import os
from ffmpy import FFmpeg
import threading


# 获取文件名称
def getName(video_path):
    return os.path.basename(video_path).split('.')[0]


# 提取并另存为
def run_ffmpeg(video_path: str, audio_path: str, format: str):
    ff = FFmpeg(inputs={video_path: None},
                outputs={audio_path: '-f {} -vn'.format(format)})
    ff.run()
    return audio_path


# 参数接受处理
def extract(video_path: str, tmp_dir: str, ext: str):
    file_name = '.'.join(os.path.basename(video_path).split('.')[0:-1])
    return run_ffmpeg(video_path, os.path.join(tmp_dir, '{}.{}'.format(getName(video_path), ext)), ext)


# 输入文件夹路径和视频名称做处理
def handle_main(video_path: str, title: str):
    """
    :param video_path: 视频文件夹路径
    :param title: 视频名称
    :return: 无
    """

    # into = extract(video_path + '/' + title + '_jm.mp4', video_path, 'mp3')
    # print(into)
    oldFullPath = video_path + '/' + title + '_jm.mp4'  # 完整的MP4路径
    jm_thread = threading.Thread(target=extract, args=(oldFullPath, video_path, 'mp3'))
    jm_thread.start()
    print('开始从MP4 转 MP3')
    jm_thread.join()
    print('转换完毕！，将 原MP4做删除处理')
    os.remove(oldFullPath)
    print('删除原MP4文件完毕！')


if __name__ == '__main__':
    root = "./"
    print(extract(root + '1.mp4', root, 'mp3'))

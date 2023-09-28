import os
from ffmpy import FFmpeg

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


if __name__ == '__main__':
    root = "./"
    print(extract(root + '1.mp4', root, 'mp3'))
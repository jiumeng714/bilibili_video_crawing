"""
把视频（或 dash 音频流）里的音频提取出来另存为 MP3。
旧版本依赖 ffmpy 且要求 ffmpeg 在 PATH 里，这里统一改成用 ffmpegTool 定位 ffmpeg。
"""

import os

from ffmpegTool import runFfmpeg


# 获取文件名称
def getName(video_path):
    return os.path.basename(video_path).split('.')[0]


def extractAudio(input_path, output_path):
    """
    从任意音视频文件里提取音频，输出 MP3。
    :param input_path: 输入文件（mp4 / m4s / flv 都可以）
    :param output_path: 输出的 mp3 路径
    :return: output_path
    """
    if os.path.exists(output_path):
        os.remove(output_path)  # 重新下载过的视频，旧的音频文件要覆盖掉
    runFfmpeg([
        '-y',
        '-i', input_path,
        '-vn', '-acodec', 'libmp3lame', '-q:a', '2',
        output_path,
    ], errorTip='提取音频失败')
    if not os.path.exists(output_path):
        raise RuntimeError('提取音频失败：没有生成 {0}'.format(output_path))
    print('音频提取完毕：' + output_path)
    return output_path


def run_ffmpeg(video_path: str, audio_path: str, format: str):
    """兼容旧接口：把视频提取成指定格式。"""
    return extractAudio(video_path, audio_path)


def extract(video_path: str, tmp_dir: str, ext: str):
    """兼容旧接口：把视频提取到 tmp_dir 下，返回输出路径。"""
    file_name = '.'.join(os.path.basename(video_path).split('.')[0:-1])
    return extractAudio(video_path, os.path.join(tmp_dir, '{}.{}'.format(file_name, ext)))


def handle_main(video_path: str, title: str):
    """
    兼容旧接口：从 {title}_jm.mp4 提取 mp3，并把原 MP4 删除。
    :param video_path: 视频文件夹路径
    :param title: 视频名称
    :return: 无
    """
    oldFullPath = os.path.join(video_path, title + '_jm.mp4')  # 完整的MP4路径
    print('开始从MP4 转 MP3')
    extractAudio(oldFullPath, os.path.join(video_path, title + '.mp3'))
    print('转换完毕！，将 原MP4做删除处理')
    os.remove(oldFullPath)
    print('删除原MP4文件完毕！')


if __name__ == '__main__':
    root = './'
    print(extract(root + '1.mp4', root, 'mp3'))

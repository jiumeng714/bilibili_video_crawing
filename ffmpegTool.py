"""
ffmpeg 定位与调用的小工具，避免 getVideo / VideoToAudio 互相 import 造成循环依赖。
"""

import os
import shutil
import subprocess
import sys


def getFfmpegPath():
    """
    找到可用的 ffmpeg：优先用项目里自带的 ffmpeg.exe，
    其次是 exe 同级目录、PATH，最后退回 imageio-ffmpeg 自带的版本。
    """
    candidates = []
    if getattr(sys, 'frozen', False):  # pyinstaller 打包后的 exe
        candidates.append(os.path.join(os.path.dirname(sys.executable), 'ffmpeg.exe'))
        candidates.append(os.path.join(getattr(sys, '_MEIPASS', ''), 'ffmpeg.exe'))
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg.exe'))
    candidates.append(os.path.join(os.getcwd(), 'ffmpeg.exe'))

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate

    onPath = shutil.which('ffmpeg')
    if onPath:
        return onPath

    try:  # moviepy 依赖的 imageio-ffmpeg 常常自带一份
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return 'ffmpeg'


def runFfmpeg(args, errorTip='ffmpeg 执行失败'):
    """
    执行一次 ffmpeg 命令，失败时抛出带 stderr 尾部的异常，方便界面上看到原因。
    :param args: ffmpeg 参数列表（不含程序本身）
    """
    command = [getFfmpegPath()] + list(args)
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        errorText = (process.stderr or b'').decode('utf-8', 'ignore')[-800:]
        raise RuntimeError('{0}：{1}'.format(errorTip, errorText))
    return process

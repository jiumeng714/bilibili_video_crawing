"""
命令行版下载器（不想要界面时用这个）。

用法示例：
    python jm_cli.py "https://www.bilibili.com/video/BV1B8rPBCELm/" -o D:/视频
    python jm_cli.py BV1BDk2YCEHF -p 2 -o D:/视频          # 下载第2个分P
    python jm_cli.py BV1B8rPBCELm -o D:/音频 --audio        # 只导出 mp3
"""

import argparse
import os
import sys

import getVideo as gv


class ConsoleText:
    """冒充界面上的文本框，把下载进度直接打到控制台。"""

    def tag_config(self, *args, **kwargs):
        pass

    def insert(self, index, content, tag=None):
        text = str(content)
        sys.stdout.write(text if text.endswith('\n') else text + '\n')
        sys.stdout.flush()

    def see(self, index):
        pass


def main():
    parser = argparse.ArgumentParser(description='B站视频 / 音频下载器（WBI 签名版）')
    parser.add_argument('url', help='视频链接、BV号或 av 号')
    parser.add_argument('-o', '--output', default='.', help='输出目录，默认当前目录')
    parser.add_argument('-p', '--page', default='1', help='第几个分P，默认1')
    parser.add_argument('--audio', action='store_true', help='只导出音频（mp3）')
    args = parser.parse_args()

    output = os.path.abspath(args.output)
    if not os.path.isdir(output):
        print('输出目录不存在：' + output)
        return 1

    global_dict = {'text': ConsoleText()}
    gv.downloadSync(args.url, output, global_dict, num=args.page,
                    isOnlyAudio=args.audio)
    return 0


if __name__ == '__main__':
    sys.exit(main())

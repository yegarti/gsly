import argparse
import sys

import youtube_dl
import requests


class YoutubeHandler:
    def __init__(self):
        self._opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    }],
                # 'progress_hooks': [my_hook],
                }

    def download(self, links, filter=lambda k: True):
        with youtube_dl.YoutubeDL(self._opts) as ydl:
            ydl.download(links)


def parse_file(filename, rtl=False):
    res = {}
    with open(filename, 'r') as f:
        data = f.readlines()
    for line in data:
        if line.strip() == '':
            continue
        lin = line.rstrip()
        if lin == lin.strip():
            res[lin] = []
            last = res[lin]
        else:
            last.append(lin.strip())
    print(res)


def build_playlist(songs_list):
    pass


def main():
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])
    parse_file(args.input, args.rtl)

    # yt = YoutubeHandler()
    # l = ['https://www.youtube.com/watch?v=gV1sw4lfwFw']
    # yt.download(l)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="List of songs")
    parser.add_argument('--rtl', dest='rtl', action='store_true', default=False, help="Songs RTL")
    return parser


if __name__ == '__main__':
    main()

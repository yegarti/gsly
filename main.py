import argparse
import sys
import logging
from difflib import SequenceMatcher
import os

import youtube_dl
import requests


API_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
API_TOKEN = os.environ['YT_API_TOKEN']

logging.basicConfig(level=logging.DEBUG, format='')
logger = logging.getLogger(__name__)


def search_query(query):
    # return results list from youtube search query

    payload = {'part': 'id,snippet', 'q': query, 'key': API_TOKEN, 'type': 'video'}
    res = requests.get(API_SEARCH_URL, params=payload)
    res.raise_for_status()
    results = res.json()
    return [{'id': item['id']['videoId'], 'title': item['snippet']['title']} for item in results['items']]


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


def parse_file(filename, simple):
    logger.debug("parse_file {} simple={}".format(filename, simple))
    res = []
    artist = ''
    with open(filename, 'r') as f:
        data = f.readlines()
    for line in data:
        if line.strip() == '':
            continue
        if simple:
            res.append(line.strip())
            logger.debug('Found "{}"'.format(res[-1]))
        else:
            lin = line.rstrip()
            if lin == lin.strip():
                artist = lin.strip()
            else:
                song = "{} {}".format(artist, lin.strip())
                res.append(song)
                logger.debug('Found "{}"'.format(res[-1]))
    return res


def get_songs(playlist, similar_rate):
    for song in playlist:
        try:
            logger.info('Querying "{}"...'.format(song))
            res = search_query(song)[0]
            similar = SequenceMatcher(None, res['title'], song).ratio()
            logger.debug('Similarity for "{}" and "{}" is {}'.format(song, res['title'], similar))
            if similar <= similar_rate:
                logger.info("Similarity is low {} < {}, Skipping {}".format(similar, similar_rate, song))
                continue
            # TODO download song in temp folder and after all is done move to output folder, check with hebrew songs
        except Exception as e:
            logger.exception(e)


def main():
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])
    logger.debug(args)
    playlist = parse_file(args.input, args.simple)
    get_songs(playlist, args.similarity)
    # yt = YoutubeHandler()
    # l = ['https://www.youtube.com/watch?v=gV1sw4lfwFw']
    # yt.download(l)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="List of songs")
    parser.add_argument('--rtl', dest='rtl', action='store_true', default=False, help="Songs RTL")
    parser.add_argument('--sim', dest='similarity', type=float, default=0.4, help="Float number between 0.0 and 1.0 that decide if a song is similiar to query (default 0.4)")
    parser.add_argument('--simple', dest='simple', action='store_true', help="File provided is in simple format (line = song)")
    return parser


if __name__ == '__main__':
    main()

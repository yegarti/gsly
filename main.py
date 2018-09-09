import argparse
import sys
import logging
from difflib import SequenceMatcher
import os

import youtube_dl
import requests


API_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
API_TOKEN = os.environ['YT_API_TOKEN']
YT_VID_URL = 'https://www.youtube.com/watch?v={}'

# logging.basicConfig(level=logging.DEBUG, format='')
logger = logging.getLogger(__name__)


def search_query(query):
    # return results list from youtube search query

    payload = {'part': 'id,snippet', 'q': query, 'key': API_TOKEN, 'type': 'video'}
    res = requests.get(API_SEARCH_URL, params=payload)
    res.raise_for_status()
    results = res.json()
    return [{'id': item['id']['videoId'], 'title': item['snippet']['title']} for item in results['items']]


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


def get_songs_id(playlist, similar_rate):
    videos_id = []
    for song in playlist:
        try:
            print('Querying "{}"...'.format(song))
            res = search_query(song)[0]
            similar = SequenceMatcher(None, res['title'], song).ratio()
            logger.debug('Similarity for "{}" and "{}" is {}'.format(song, res['title'], similar))
            if similar <= similar_rate:
                print("Similarity is low {} < {}, Skipping {}".format(similar, similar_rate, song))
                continue
            videos_id.append(res['id'])
            print('Added "{}"'.format(res['title']))
            logger.debug('Added video id {} to results'.format(res['id']))
        except Exception as e:
            logger.exception(e)
    return videos_id


def download_songs(songs_id, out_dir):
    def hook(d):
        name = os.path.basename(d['filename'].rpartition('.')[0])
        if d['status'] == 'downloading':
            sys.stdout.write('\rDownloading: {} - {}'.format(name, d['_percent_str']))
            sys.stdout.flush()
        elif d['status'] == 'finished':
            sys.stdout.write('\rFinished: {} -   100%\n'.format(name))
            sys.stdout.flush()

    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            logger.error(msg)

    ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(out_dir, '%(title)s.$(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            'progress_hooks': [hook],
            'logger': MyLogger()
            }

    songs_id = [YT_VID_URL.format(id) for id in songs_id]
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(songs_id)


def main():
    args = get_parser().parse_args(sys.argv[1:])
    logger.debug(args)
    if not os.path.exists(args.output):
        logger.error("ERROR: Path '{}' does not exist".format(args.output))
        sys.exit(1)
    playlist = parse_file(args.input, args.simple)
    ids = get_songs_id(playlist, args.similarity)
    download_songs(ids, args.output)
    print("Done!")
    # yt = YoutubeHandler()
    # l = ['https://www.youtube.com/watch?v=gV1sw4lfwFw']
    # yt.download(l)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="List of songs")
    parser.add_argument('--sim', dest='similarity', type=float, default=0.4, help="Float number between 0.0 and 1.0 that decide if a song is similiar to query (default 0.4)")
    parser.add_argument('--simple', dest='simple', action='store_true', help="File provided is in simple format (line = song)")
    parser.add_argument('--output', '-o', default=os.getcwd(), dest='output', help="Output directory to place songs")
    return parser


if __name__ == '__main__':
    main()

import json
import requests
import re
import sys

from tqdm import tqdm


class API():
    ARTIST_RE = re.compile(r'artist: "(.+)",')
    ALBUM_RE = re.compile(r'album_title: "(.+)",')
    TRACKS_RE = re.compile(r'trackinfo : (.+),\n')
    FORBIDDEN_RE = re.compile(r'[^\w\d]')

    def __init__(self, url):
        self.url = url
        self.album = ''
        self.artist = ''
        self.tracks = {}

    def get_infos(self):
        resp = requests.get(self.url)
        if resp.status_code != 200:
            return False

        r = re.search(self.ARTIST_RE, resp.content)
        if r:
            self.artist = r.group(1)

        r = re.search(self.ALBUM_RE, resp.content)
        if r:
            self.album = r.group(1)

        r = re.search(self.TRACKS_RE, resp.content)
        if r:
            json_resp = json.loads(r.group(1))
            for element in json_resp:
                self.tracks[element['title']] = element['file']['mp3-128']


    def download_all(self):
        for i, name in enumerate(self.tracks):
            self.download(name, i, len(self.tracks))

    def download(self, name, i, count):
        filename = '%s.mp3' % self.FORBIDDEN_RE.sub('_', name)

        resp = requests.get(self.tracks[name], stream=True)
        total_length = int(resp.headers.get('Content-Length', 0))
        desc = '%d/%d %s' % (i+1, count, name)
        with open(filename, 'w') as f:
            for chunk in tqdm(resp.iter_content(), total=total_length, desc=desc):
                f.write(chunk)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('python %s <url>' % sys.argv[0])
        sys.exit(1)

    api = API(sys.argv[1])
    api.get_infos()
    api.download_all()

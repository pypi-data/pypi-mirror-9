#!/usr/bin/env python
# coding=utf-8

import os
import requests
import json

# 'ascii' codec can't encode characters
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except :
    pass

try:
    from downloadhelper import Download
except :
    pass

from .player import BasePlayer as Player

class MusicDownload(object):

    def __init__(self, play=False):
        self.__SONG_DATA_URL = r'http://music.baidu.com/data/music/fmlink?songIds='
        self.__SONG_REAL_URL = None

        # Song info
        self.__SONG_ID = None
        self.__SONG_NAME = None
        self.__SONG_AUTHOR = None
        self.__SONG_FORMAT = None
        self.__SONG_ALBUM = None

        # play music
        self.__play = play

    def get_real_song_data(self, song_id):
        self.__SONG_ID = song_id
        data_url = self.__SONG_DATA_URL+str(self.__SONG_ID)
        req = requests.get(data_url)

        try:
            song_data_json = json.loads(req.content)
        except TypeError:
            if req.encoding:
                song_data_json = json.loads(req.content\
                                        .decode(req.encoding))
            else:
                song_data_json = json.loads(req.content\
                                        .decode(req.apparent_encoding))

        song_data = song_data_json.get('data', None)
        if song_data == None:
            return 

        if song_data != '':
            songList = song_data['songList'][0]
            self.__SONG_NAME = songList['songName'].replace('/', '-')
            self.__SONG_AUTHOR = songList['artistName'].replace('/', '-')
            self.__SONG_FORMAT = songList['format']
            self.__SONG_ALBUM = '' if songList['albumName'] == None else songList['albumName'].replace('/', '-')
            self.__SONG_REAL_URL = songList['songLink']
        
        self.__SONG_REAL_DATA = song_data
        return self.__SONG_REAL_DATA
            
    def download_song(self, song_id, path='.', id=0, ids=0):
        # Cannot Find Or download This song
        self.get_real_song_data(song_id)
        mp3Name = "{songName}--{author}.{format}".format(
            songName = self.__SONG_NAME,
            author = self.__SONG_AUTHOR,
            format = self.__SONG_FORMAT,
            ).strip()

        download_flag = [0, 0, 0, 'unknownfilename']
        if not self.__SONG_REAL_URL:
            print("No valid Url.")
        else:
            if not self.__play:
                download = Download(modified=False)
                download_flag = download.download(self.__SONG_REAL_URL, 
                                              mp3Name, path, id, ids)
            else :
                sys.stdout.write('稍等, 正在缓冲 %s...\n' 
                                 % mp3Name.split('.')[0])
                sys.stdout.flush()
                download = Download(modified=False, quiet=True)
                download_flag = download.download(self.__SONG_REAL_URL, 
                                              mp3Name, path, id, ids)
                sys.stdout.write('Playing %s ...\n' % mp3Name.split('.')[0])
                sys.stdout.flush()
                handler = Player(os.path.join(path, mp3Name)).start()
                handler.wait()

        download_flag = list(download_flag)
        download_flag[3] = os.path.join(path, mp3Name)
        return download_flag

    def get_real_song_url(self, song_id):
        '''
            url
        '''
        self.get_real_song_data(song_id)
        return self.__SONG_REAL_URL

    def get_song_name(self, song_id):
        '''
            name
        '''
        self.get_real_song_data(song_id)
        return self.__SONG_NAME

    def get_song_author(self, song_id):
        self.get_real_song_data(song_id)
        return self.__SONG_AUTHOR

    def get_song_album(self, song_id):
        self.get_real_song_data(song_id)
        return self.__SONG_ALBUM


if __name__ == '__main__':
    import sys
    
    Baidu = MusicDownload()
    if len(sys.argv) == 1:
        print("Usage:")
        print("\t{filename} Song_id".format(filename=sys.argv[0]))
        print("\t{filename} song_id1 song_id2 ...".format(filename=sys.argv[0]))
        exit(False)

    for song_id in sys.argv:
        if song_id == sys.argv[0]:
            continue
        Baidu.download_song(song_id)

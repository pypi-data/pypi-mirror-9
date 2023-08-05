#!/usr/bin/env python
# coding=utf-8

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
    input = raw_input
except:
    pass
import os
import re
import json
from datetime import date

try:
    import requests
    from prettytable import PrettyTable
    from bs4 import BeautifulSoup
except:
    pass

from .BaiduMusicUtils import MusicDownload
from .player import BasePlayer as Player

class BaiduMusic:
    
    VERSION = '0.2.1'

    def __init__(self, play=False, play_around=False, *args, **kwargs):
        # @args
        # 1. play
        # 2. play around
        self.__BASE_URL = {
            'album': r'http://music.baidu.com/album/{para}',
            'artist': r'http://music.baidu.com/artist/{para}',
            'moreabout': r'http://music.baidu.com/search/song?'+
                's=1&key={para}&jump=0&start={start}&size=20',
            'author': r'http://music.baidu.com/search?key={para}',
            'find': r'http://music.baidu.com/search/song?' + \
                    's=1&key={para}&start={start}&size=20',
            'song': r'http://music.baidu.com/song/{para}',
            'songlist': r'http://music.baidu.com/songlist/{para}',
            'songlist-info': r'http://music.baidu.com/songlist',
            'tag': r'http://music.baidu.com/tag/{para}?start=0&size=25',
            'info': 'http://sug.music.baidu.com/info/suggestion?'+\
                    'format=json&word={para}',
        }

        self.__start = 0
        self.__type = None
        self.__para = None

        self.__store_dir_re = None;

        self.__source_url = None # 原始链接
        self.__req_content = None # 请求页面的内容
        self.__song_id_list = [] # 列表, 歌的ID
        self.__song_number = 0 # 几首歌

        self.__home_dir = os.environ.get('HOME', '.')
        self.__default_base_dir = os.path.join(self.__home_dir, 'Music/BdMusic')
        self.__store_dir = str(date.today()) 

        self.__doplay = play
        self.__play_around = play_around
        self.__page_number = 5 # default 5

    def set_do_play(self, play=False):
        if play:
            self.__doplay = play
            self.__page_number = 1

    def info_author(self):
        assert self.__source_url
        self.get_source_html()

        jsonData = json.loads(self.__req_content)
        artistData = jsonData.get('artist')
        albumData = jsonData.get('album')
        songData = jsonData.get('song')

        artist_table = PrettyTable(['', '歌手', 'ID'])
        for each in artistData:
            artist_table.add_row([artistData.index(each)+1, 
                                  each.get('artistname'), 
                                  each.get('artistid')])

        album_table = PrettyTable(['', '专辑', 'ID'])
        for each in albumData:
            album_table.add_row([albumData.index(each)+1,
                                 each.get('albumname'), 
                                 each.get('albumid')])

        song_table = PrettyTable(['', '歌名', '歌手', '歌曲ID'])
        for each in songData:
            song_table.add_row([songData.index(each)+1,
                                each.get('songname'), 
                                each.get('artistname'), 
                                each.get('songid')])

        # display
        print(artist_table)
        print(album_table)
        print(song_table)

    def info_songlist(self):
        id = 0
        while True:
            self.info_songlist_next(id)
            id += 1
            answer = input('Next page ? (y|N)')
            if answer not in ['y', 'yes', 'Yes', 'Y']:
                return 

    def info_songlist_next(self, page=0):
        assert self.__source_url

        html = ''
        if page == 0:
            url = self.__source_url
            html = requests.get(url).content
        else:
            url = r'http://music.baidu.com/data/music/songlist/list?start=%s&size=8&tagname=' % (page * 20)
            jsonData = requests.get(url)\
                    .json().get('data').get('collectList')
            for each in jsonData:
                html += each

        htmlB = BeautifulSoup(html)
        songlist_html = htmlB.findAll(name='a', 
                                      attrs={'class': 'title-link'})
        songlist_table = PrettyTable(['', 'ID', '歌单'])

        for each in songlist_html:
            nu = songlist_html.index(each) + 1
            id = re.findall(r'/songlist/(\d+)', each.attrs.get('href'))[0]
            name = each.text.strip()
            songlist_table.add_row([nu, id, name])

        # display
        print(songlist_table)

    def search(self):
        assert self.__req_content
        
        id_name_reg = r'data-songdata=[\'"]{ "id": "([^"]+)" }\S*title="([^"]+)"';
        author_reg = r'<span class="author_list" title="([^"]+)">';
        ids_and_names = re.findall(id_name_reg, self.__req_content)
        authors = re.findall(author_reg, self.__req_content)
        id_name_authors = []
        ID = 0
        for i_n in ids_and_names:
            if ID < len(authors):
                i_n_a = (i_n[0], i_n[1], authors[ID])
                ID += 1
            else:
                i_n_a = (i_n[0], i_n[1], '')
            id_name_authors.append(i_n_a)
        #print('   ' +
        #      'ID'.ljust(15, ' ') +
        #      ' Name'.ljust(15, ' ') +
        #      ' Author'.ljust(15, ' '))
        table = PrettyTable(['ID', 
                             'SongID', 
                             'Name', 
                             'Author'])
        ID = 1
        for i_n_a in id_name_authors:
            #print(str(ID).ljust(2) + ' ' + 
            #      i_n_a[0].ljust(15, ' ') +
            #      i_n_a[1].ljust(20, ' ') +
            #      i_n_a[2].ljust(15, ' ')
            #     )
            table.add_row([ID, 
                           i_n_a[0], 
                           i_n_a[1], 
                           i_n_a[2]])
            ID += 1
        print(table)

        # No next Page
        if len(id_name_authors) < 20:
            return 
        # Next Page
        self.search_next_page()

    def search_next_page(self):
        try:
            answer = raw_input("Would you like to go to next Page ?[y|N]")
        except NameError:
            answer = input("Would you like to go to next Page ?[y|N]")
        if answer != "y" and answer != "Y" \
           and answer != "yes" and answer != "Yes":
            return
        self.__start += 20
        self.__source_url = self.__BASE_URL['find'].\
            format(para=self.__para, start=self.__start)
        self.get_source_html()
        self.search()

    def set_url(self, type, para):
        self.__type = type
        self.__para = para

        if self.__type in ['find', 'moreabout']:
            self.__source_url = self.__BASE_URL[type].\
                    format(para=self.__para, start=self.__start)
        else:
            self.__source_url = self.__BASE_URL[type].format(para=para)

        self.__store_dir_re = {
            # 'album': 'album_' + self.__para,
            'album': r'<h2 class="album-name">([^"]+)</h2>',
            'artist': r'<h2 class="singer-name">([^"]+)</h2>',
            'moreabout': 'moreabout_{0}'.format(self.__para),
            'author': self.__para,
            'find': r'Song',
            'song': r'Song',
            'songlist': r'<h2>([^"]+)</h2>', # r'</span>([^"]+)</h2>'),
            'songlist-info': 'SongList',
            'tag': '<span class="title">([^"]+)</span>',
            'info': r'AuthorInfo',
        }

    def set_store_dir(self, type):
        if type != 'song':
            assert self.__req_content

        # if type in ('album', 'author', 'song'):
        if type in ('author', 'song', 'moreabout', 'info'):
            self.__store_dir = self.__store_dir_re[type]
            return

        dirname_list = re.findall(self.__store_dir_re[type], 
                                      self.__req_content)
        if dirname_list == []:
            dirname_list = re.findall(r'</span>([^"]+)</h2>', 
                                      self.__req_content)
        if dirname_list != []:
            self.__store_dir = dirname_list[0].strip()

        if type in ('album', ):
            self.__store_dir = os.path.join(r'专辑', 
                                            self.__store_dir)
        if type in ('songlist', ):
            self.__store_dir = os.path.join(r'歌单', 
                                            self.__store_dir)


    def get_source_html(self):
        assert self.__source_url
        if self.__type == 'song':
            self.__song_id_list = [ self.__para ]
            self.__song_number = 1
            return -1

        if self.__type in ['artist']:
            self.__req_content = ''
            self.__req_content += requests.get(self.__source_url).text
            start = 25
            for i in range(self.__page_number):
                source_url = r'http://music.baidu.com/data/user/getsongs?start=%s&ting_uid=%s' % (start, self.__para)
                req = requests.get(source_url)
                errorCode = req.json().get('errorCode')
                if errorCode != 22000:
                    return 
                html = req.json().get('data').get('html')
                self.__req_content += html
                start += 25
            return

        if self.__type in ['moreabout']:
            self.__req_content = ''
            self.__req_content += requests.get(self.__source_url).text
            start = 20
            for i in range(self.__page_number):
                source_url = self.__BASE_URL['moreabout'].format(\
                                        para=self.__para, start=start)
                req = requests.get(source_url)
                self.__req_content += req.content
                start += 20
            return

        req = requests.get(self.__source_url)
        self.__req_content = req.text

    def get_song_id_list(self):
        assert self.__source_url

        if self.__para in ['info']:
            return 

        if self.get_source_html() == -1:
            return 

        source_html = self.__req_content
        song_id_list = []
        #if self.__type != 'songlist':
        song_id_list = re.findall(r'data-ids="([^"]+)"', source_html)
        try:
            song_id_list = song_id_list[0].replace(' ', '').split(',')
        except IndexError:
            #sys.stdout.write('IndexError 404: No song found.\n')
            #sys.stdout.flush()
            #sys.exit()
            pass
        #if song_id_list == []:
        song_id_list += re.findall(r'<a href="/song/(\d+).*"',
                                      source_html)

        self.__song_id_list = list(set(song_id_list))
        self.__song_number = len(self.__song_id_list)

    def download(self, type, para):
        self.set_url(type, para)
        self.get_song_id_list()
        self.set_store_dir(type)

        if self.__type == 'info':
            self.info_author()
            return

        if self.__type == 'songlist-info':
            self.info_songlist()
            return

        if not self.__song_number:
            sys.stdout.write('IndexError 404: No song found.\n')
            sys.stdout.flush()
            return

        if self.__type == 'find':
            self.search()
            return 

        # if self.__doplay:
        #    self.__store_dir = '播放过的音乐'
        self.__store_dir = os.path.join(self.__default_base_dir, 
                                        self.__store_dir)
        if not os.path.exists(self.__store_dir):
            # os.mkdir(self.__store_dir)
            os.makedirs(self.__store_dir)

        print('Dir: %s' % self.__store_dir)
        print('Length: 总共%d首歌' % self.__song_number)
        id = 1
        all_files = []
        for song_id in self.__song_id_list:
            md = MusicDownload(play=self.__doplay)
            status = md.download_song(song_id, self.__store_dir, id, 
                                self.__song_number)
            if status[2] >= 0:
                id += 1

            file_name = status[3]
            if self.__doplay and file_name:
                all_files.append(file_name)
                sys.stdout.write('Playing %s ...\n' % 
                                 file_name.split('/').pop()\
                                    .replace('.mp3', ''))
                sys.stdout.flush()
                try:
                    handler = Player(file_name).start()
                    handler.wait()
                except KeyboardInterrupt:
                    print('\nOMG, 你竟然主动终止播放!!!太伤心了！多角落哭泣！\n')
                    sys.exit(-1)
        
        while self.__play_around:
            for each in all_files:
                sys.stdout.write('Playing %s ...\n' % 
                                 each.split('/').pop()\
                                    .replace('.mp3', ''))
                sys.stdout.flush()
                try:
                    handler = Player(each).start()
                    handler.wait()
                except KeyboardInterrupt:
                    print('\nOMG, 你竟然主动终止播放!!!太伤心了！多角落哭泣！\n')
                    sys.exit(-1)
        

    @staticmethod
    def usage(command):
        print('NAME:')
        print('  %s - The Baidu Music Download Class write by python.\n' % command)
        print('DESCRIPTION:')
        print('  %s is a Simple Baidu Music Download Class write by python depends \
              on python-requests. Authored by Cole Smith.\n' % command)
        print('USAGE:')
        print('  %s OPTIONS Pareters\n' % command)
        print('OPTIONS:')
        print('  -a, --album ID         Download By album id.')
        print('  -f, --find keyword     Download By song id.')
        print('  -h, --help             Get help about usage and description.')
        print('  -i, --info authorname  Get author info.')
        print('  -k, --songlist info    Get songlist info.')
        print('  -l, --songlist ID      Download By songlist id.')
        print('  -m, --moreabout keyword Download more about keyword.')
        print('  -n, --author Name      Download By author name.')
        print('  -p, --play             Specify the filepath where you want to store the file')
        print('  -q, --play_around      Play Around.')
        print('  -r, --artist ID        Download By artist id.')
        print('  -s, --song ID          Download By song id.')
        print('  -t, --tag Name         Download By tag name.')
        print('  -u, --url URL          Your download file\'s url.')
        print('  -v, --version          Get download class version.')
        print('')

    @staticmethod
    def version(command):
        sys.stdout.write('%s Version %s\n' % (sys.argv[0], BaiduMusic.VERSION))
        sys.stdout.flush()

def main():
    import getopt
    
    opts = []
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'a:r:m:n:hi:pqs:kl:t:u:vf:',
            ['album=', 'artist=', 'moreabout=', 'author=', 'help', 
             'info=', 'play', 'play_around', 'song=', 
             'songlist-info', 'songlist=', 'tag=', 
             'url=', 'version', 'find=']
            )
    except getopt.GetoptError:
        sys.stdout.write('Get Opt Error\n')
        sys.stdout.write('%s -h for help\n' % sys.argv[0])
        sys.stdout.flush()
        sys.exit()
    finally: 
        if opts == []:
            BaiduMusic.usage(sys.argv[0])
            sys.exit()

    ID = None
    Type = None
    Url = None
    Play = False
    PlayAround = False
    
    for o, a in opts:
        if Type != None:
            break

        if o in ('-h', '--help'):
            BaiduMusic.usage(sys.argv[0])
            sys.exit()
        if o in ('-v', '--version'):
            BaiduMusic.version(sys.argv[0])
            sys.exit()
        if o in ('-a', '--album'):
            Type = 'album'
            ID = a
        if o in ('-l', '--songlist'):
            Type = 'songlist'
            ID = a
        if o in ('-r', '--artist'):
            Type = 'artist'
            ID = a
        if o in ('-s', '--song'):
            Type = 'song'
            ID = a
        if o in ('-n', '--author'):
            Type = 'author'
            ID = a
        if o in ('-u', '--url'):
            Type = 'url'
            Url = a
        if o in ('-t', '--tag'):
            Type = 'tag'
            ID = a
        if o in ('-f', '--find'):
            Type = 'find'
            ID = a
        if o in ('-m', '--moreabout'):
            Type = 'moreabout'
            ID = a
        if o in ('-i', '--info'):
            Type = 'info'
            ID = a
        if o in ('-p', '--play'):
            Play = True
        if o in ('-q', '--play_around'):
            PlayAround = True
        if o in ('-k', '--songlist-info'):
            Type = 'songlist-info'
            ID = 'nonono'
            
    if Type == 'url':
        uu = re.findall(r'http://music.baidu.com/([^/"]+)', Url)
        oo = re.findall(r'http://music.baidu.com/\w+/(.[^/?]+)', Url)
        if uu == [] or oo == []:
            print('Error: Invalid Url')
            sys.exit()
        Type = uu[0]
        ID = oo[0]
    
    if not Type or not ID:
        print('Error: Type Or ID Invalid')
        sys.exit(-1)
    # Main
    BdMusic = BaiduMusic(Play, PlayAround)
    # BdMusic.set_do_play(Play)
    BdMusic.download(Type, ID)

if __name__ == '__main__':
    main()

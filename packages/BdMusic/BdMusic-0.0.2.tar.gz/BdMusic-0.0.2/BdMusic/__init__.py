# coding=utf-8

import sys
import getopt
import re

from .BaiduMusic import BaiduMusic

def main():
    opts = []
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'a:r:m:n:hp:s:l:t:u:vf:',
            ['album', 'artist', 'moreabout', 'author', 'help', 
             'path', 'song', 'songlist', 'tag', 
             'url', 'version', 'find']
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
    Name = None
    
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
            global Name
            Name = a
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
    BdMusic = BaiduMusic()
    BdMusic.download(Type, ID)


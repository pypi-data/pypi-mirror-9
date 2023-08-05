# coding=utf-8

import sys
import getopt

from .downloadhelper import Download
from .downloadhelper import MultiDownloadThread
from .downloadhelper import VERSION

download_class = Download

def download(url, file_name, file_path=None, id=1, ids=1):
    """
    download main
    return (all_size, need_download_size, flag)
    flag:
        0  Success, download
        1  Success, and alread downloaded
        2  Success, and modified , then redownload
        -1 Failed, and Request but not response
        -2 Failed, and connection Error
        -3 Failed, and Request Times Out; Default Times = Twice(2)
        -4 Failed, and downloading then socket.timeout

    For Example:
        a = download(url, file_name[, id, ids])
        print(a)
        help(a)
    """
    oo = Download()
    return oo.download(url, file_name, file_path, id, ids)

def multidownload(url, file_name, file_path, id=1, ids=1):
    """
        multiple threads download
    """
    oo = MultiDownloadThread()
    return oo.download(url, file_name, file_path, id, ids)        

def main():
    '''Command Line'''
    opts = ''
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hu:n:p:i:v:',
            ['help', 'url', 'name', 'path', 'id', 'version']
            )
    except getopt.GetoptError:
        sys.stdout.write('Get Opt Error\n')
        sys.stdout.write('%s -h for help\n' % sys.argv[0])
        sys.stdout.flush()
        sys.exit(-1)
    finally:
        if opts == []:
            Download.usage(sys.argv[0])
            sys.exit()

    url = None
    name = None
    path = None
    id = 0
    for o, a in opts:
        if o in ('-h', '--help'):
            Download.usage(sys.argv[0])
            sys.exit()
        if o in ('-v', '--version'):
            sys.stdout.write('%s Version %s\n' % (sys.argv[0].split('/').pop(), VERSION))
            sys.stdout.flush()
            sys.exit()
        if o in ('-u', '--url'):
            url = a
        if o in ('-n', '--name'):
            name = a
        if o in ('-p', '--path'):
            path = a
        if o in ('-i', '--id'):
            id = int(a)

    if url==None or name==None:
        sys.stdout.write('url and file name must be specified\n')
        sys.stdout.flush()
        sys.exit()

    OO = Download()
    OO.download(url, name, path, id)

def get():
    if len(sys.argv) <= 1:
        print('Usage:\n\t%s URL' % sys.argv[0].split('/').pop())
        return

    url = sys.argv[1]
    name = url.split('/').pop()

    OO = Download()
    OO.download(url, name, '.', 1)

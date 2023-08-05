# coding=utf-8

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

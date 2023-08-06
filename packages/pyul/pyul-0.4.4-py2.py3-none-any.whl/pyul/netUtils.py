import urllib2
from urlparse import urlsplit
from pathlib import Path

from pyul import coreUtils
from pyul.support import Path

__all__ = ['download_file']


def download_file(url, local_dir=None):
    url_file_name = Path(urlsplit(url)[2]).name
    if local_dir is None:
        local_dir = coreUtils.getUserTempDir()
    url_local_path = Path(local_dir).joinpath(url_file_name)
    fullurl = urllib2.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    url_file_handle = urllib2.urlopen(fullurl)
    with open(str(url_local_path),'wb') as file_handle :
        file_handle.write(url_file_handle.read())
    
    return url_local_path
    
if __name__ == '__main__':
    download_file('http://download.thinkbroadband.com/5MB.zip')
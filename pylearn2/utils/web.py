__authors__ = "Trung Huynh"
__copyright__ = "(c) 2010, Universite de Montreal"
__license__ = "3-clause BSD license"
__contact__ = "trunghlt@gmail.com"

import os
import logging
import urllib2
import zipfile
from tempfile import NamedTemporaryFile

log = logging.getLogger(__name__)

def download(url, dest, fname):
    """ Download file to `dest` and name it as `fname` """
    if not os.path.exists(dest):
        os.makedirs(dest)
    fpath = os.path.join(dest, fname)
    with open(fpath, "w") as f:
        response = urllib2.urlopen(url)
        f.write(response.read())
        f.close()

def unzip(url, dest):
    """
    Download original data and unzip it to data path

    """
    response = urllib2.urlopen(url)
    content = response.read()
    with NamedTemporaryFile(delete=False) as f:
        f.write(content)
        f.close()
        log.debug('Downloaded content has been saved to {}'.format(f.name))
        with open(f.name) as g:
            zfile = zipfile.ZipFile(g)
            for name in zfile.namelist():
                log.debug(
                    'Decompressing {} to {}'.format(name, dest))
                zfile.extract(name, dest)
            g.close()

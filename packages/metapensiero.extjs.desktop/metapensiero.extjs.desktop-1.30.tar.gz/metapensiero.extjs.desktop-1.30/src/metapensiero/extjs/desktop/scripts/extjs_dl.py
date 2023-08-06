# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.extjs.desktop -- ExtJS downloader
# :Creato:    dom 16 feb 2014 13:54:41 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

URL = 'http://cdn.sencha.com/ext/gpl/ext-4.2.1-gpl.zip'


def download_and_extract(url, replace=False, cache=None, all=False, src=False):
    "Download and extract ExtJS under assets/extjs."

    try:
        from io import BytesIO
    except ImportError:
        from cStringIO import StringIO as BytesIO
    from hashlib import md5
    from os import makedirs
    from os.path import dirname, exists, join, normpath
    from pkg_resources import resource_filename
    from shutil import copyfileobj, rmtree
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen
    from zipfile import ZipFile

    d = resource_filename('metapensiero.extjs.desktop', 'assets/extjs')
    if exists(d):
        if replace:
            print('Removing existing %s...' % d)
            rmtree(d)
        else:
            print('%s already present!' % d)
            return

    f = None
    if cache is not None:
        hashurl = md5(url.encode()).hexdigest()
        cached = normpath(join(cache, hashurl))
        if exists(cached):
            print('Reusing cached archive %s' % cached)
            f = open(cached, 'rb')

    if f is None:
        print('Fetching %s...' % url)
        try:
            f = urlopen(url)
        except IOError:
            print('Could not fetch ExtJS archive from %s!' % (url,))
            return
        else:
            if cache is not None:
                if not exists(cache):
                    makedirs(cache)
                with open(cached, 'wb') as c:
                    copyfileobj(f, c)
                f = open(cached, 'rb')

    print('Extracting %s into %s...' % (url, d))

    z = ZipFile(BytesIO(f.read()))
    names = z.namelist()

    for n in sorted(names):
        if n.endswith('/'):
            continue
        # Extract just what's needed
        outn = n.partition('/')[2]
        if not outn:
            continue
        if all or outn.startswith('resources/') or (
                src and (outn.startswith('src/') or outn == 'ext-dev.js')):
            f = normpath(join(d, outn))
            outd = dirname(f)
            if not exists(outd):
                makedirs(outd)
            with open(f, 'wb') as o:
                o.write(z.read(n))

# -*- coding: utf-8 -*-
#:Progetto:  metapensiero.extjs.desktop -- ExtJS downloader
#:Creato:    mar 02 apr 2013 10:21:38 CEST
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

from .scripts.extjs_dl import URL, download_and_extract


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description=download_and_extract.__doc__)
    parser.add_argument('--cache', metavar="DIR",
                        help="Cache the ExtJS zip archive under directory DIR"
                        " instead of downloading it each time")
    parser.add_argument('--replace', action='store_true', default=False,
                        help="Remove previously extracted framework")
    parser.add_argument('--url', metavar="URL", default=URL,
                        help="Download ExtJS archive from the given URL"
                        " instead of using the default (%s)" % URL)
    parser.add_argument('--all', action='store_true', default=False,
                        help="Extract everything instead of just the resources")
    parser.add_argument('--src', action='store_true', default=False,
                        help="Extract also the development sources")

    args = parser.parse_args()
    download_and_extract(args.url, replace=args.replace, cache=args.cache,
                         all=args.all, src=args.src)

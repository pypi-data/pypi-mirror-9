# -*- coding: utf-8 -*-
#:Progetto:  metapensiero.extjs.desktop
#:Creato:    mar 11 dic 2012 10:03:12 CET
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

import os
from codecs import open

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

setup(
    name='metapensiero.extjs.desktop',
    version=VERSION,
    description="An ExtJS 4 desktop application packaged with extra goodies",
    long_description=README + u'\n\n' + CHANGES,

    author='Lele Gaifax',
    author_email='lele@metapensiero.it',
    url="https://bitbucket.org/lele/metapensiero.extjs.desktop",

    license="GPLv3+",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "License :: OSI Approved ::"
        " GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['metapensiero', 'metapensiero.extjs'],

    install_requires=[
        'setuptools',
    ],

    extras_require={
        'dev': [
            'pyramid',
            'Versio',
        ]
    },

    message_extractors={
        'src/metapensiero/extjs/desktop/assets/js': [
            ('**.js', 'javascript', None),
        ],
        'src/metapensiero/extjs/desktop/templates': [
            ('extjs-l10n.mako', 'javascript', None),
        ]
    },

    zip_safe=False,

    entry_points="""\
    [console_scripts]
    minify_js_scripts = metapensiero.extjs.desktop.scripts.minifier:main
    bump_version = metapensiero.extjs.desktop.scripts.bumper:main
    [pyramid.scaffold]
    desktop=metapensiero.extjs.desktop.pyramid:DesktopProjectTemplate
    """,
)

# $Id: setup.py 27712e4d14f8 2014/11/10 10:44:22 Patrick $
"""Setup for PubliForge."""

import os

from setuptools import setup, find_packages, Extension

VERSION = '1.2'
PROJECT = 'PubliForge'

REQUIRES = [
    'pyramid>=1.5',
    'pyramid_beaker>=0.8',
    'pyramid_rpc>=0.5.2',
    'pyramid_chameleon>=0.3',
    'WebHelpers2<2.0b5',
    'colander>=0.9.9',
    'SQLAlchemy>=0.9',
    'psycopg2>=2.5',
    'lxml>=3.3',
    'pycrypto>=2.6',
    'Mercurial>=2.9',
    'hgsubversion>=1.6',
    'subvertpy>=0.9',
    'docutils>=0.11',
    'Pygments>=1.6',
    'Whoosh>=2.6',
    'Babel>=0.9.6',
    'waitress>=0.8',
    'pyramid_debugtoolbar>=2.0',
    'WebTest>=2.0',
    'WebError>=0.10',
]

HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.txt')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.txt')).read()

setup(
    name=PROJECT,
    version=VERSION,
    description='Online multimedia publishing system',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Patrick PIERRE',
    author_email='patrick.pierre@prismallia.fr',
    url='www.publiforge.org',
    keywords='web wsgi bfg pylons pyramid publiforge',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='publiforge',
    install_requires=REQUIRES,
    ext_modules=[Extension(
        'publiforge.lib.rsync._librsync',
        ['publiforge/lib/rsync/_librsync.c'],
        libraries=['rsync'])
    ],
    message_extractors={'publiforge': [
        ('**.py', 'python', None),
        ('**.pt', 'mako', {'input_encoding': 'utf-8'}),
    ]},
    entry_points="""\
    [paste.app_factory]
    main = publiforge:main

    [console_scripts]
    pfpopulate = publiforge.scripts.pfpopulate:main
    pfbackup = publiforge.scripts.pfbackup:main
    pfbuild = publiforge.scripts.pfbuild:main
    pftexmath = publiforge.scripts.pftexmath:main
    pfimage2svg = publiforge.scripts.pfimage2svg:main
    pfminify = publiforge.scripts.pfminify:main
    """,
)

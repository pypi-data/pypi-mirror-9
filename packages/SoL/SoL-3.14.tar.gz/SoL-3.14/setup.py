# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    lun 13 ott 2008 16:57:57 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
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

requires = [
    'Babel',
    'Pillow',
    'PyYAML',
    'SQLAlchemy',
    'alembic',
    'cryptacular',
    'metapensiero.extjs.desktop',
    'metapensiero.sqlalchemy.proxy',
    'pycountry',
    'pygal',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_mako',
    'pyramid_tm',
    'reportlab',
    'setuptools',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
    ]

setup(
    name='SoL',
    version=VERSION,
    description="Carrom tournaments management",
    long_description=README + u'\n\n' + CHANGES,

    author="Lele Gaifax",
    author_email="lele@metapensiero.it",
    url="https://bitbucket.org/lele/sol",

    license="GPLv3+",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: JavaScript",
        "Operating System :: OS Independent",
        "Framework :: Pyramid",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved ::"
        " GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Natural Language :: Italian",
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
    keywords='web wsgi bfg pylons pyramid',

    packages=['alembic'] + find_packages('src'),
    package_dir={'': 'src',
                 'alembic': 'alembic'},

    include_package_data=True,

    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=requires,

    entry_points="""\
    [paste.app_factory]
    main = sol:main

    [console_scripts]
    soladmin = sol.scripts.admin:main
    """,
)

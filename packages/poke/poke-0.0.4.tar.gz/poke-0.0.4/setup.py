#!/usr/bin/env python
import os
from setuptools import setup, find_packages


version = '0.0.4'


# monkey patch os for vagrant hardlinks
del os.link


# prepare config
config = dict(

    # author
    author = 'Dmitry Belyakov',
    author_email='dmitrybelyakov@gmail.com',

    # project meta
    name = 'poke',
    version=version,
    url = 'https://github.com/projectshift/poke',
    download_url='https://github.com/projectshift/poke/tarball/'+version,
    description='Simple server to listen on port and touch configured files',
    keywords=['inotify', 'server'],

    # license
    license = 'MIT',

    # packages
    packages = find_packages(exclude=['tests']),

    # dependencies
    install_requires = [
        'bottle==0.12.8',
        'argparse>=1.1',
        'bottle==0.12.8',
        'PyYAML.Yandex>=3.10.0'
    ],

    # entry points
    entry_points = dict(
        console_scripts = [
            'poke = poke.poke:main'
        ]
    )


)

# finally run the setup
setup(**config)

# register: ./setup.py register -r pypi
# build: ./setup.py sdist
# upload: ./setup.py upload -r pypi
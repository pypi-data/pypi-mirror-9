#!/usr/bin/env python

from setuptools import setup

def read_description():
    import os
    path = os.path.join(os.path.dirname(__file__), 'README.rst')
    try:
        with open(path) as f:
            return f.read()
    except:
        return 'No description found'

setup(
    name='autotorrent',
    version='1.2.3',
    description='AutoTorrent allows easy cross-seeding',
    long_description=read_description(),
    author='Anders Jensen',
    author_email='johndoee+autotorrent@tidalstream.org',
    maintainer='John Doee',
    url='https://github.com/JohnDoee/autotorrent',
    packages=['autotorrent'],
    install_requires=['BitTorrent-bencode'],
    license='BSD',
    entry_points={ 'console_scripts': [
        'autotorrent = autotorrent.cmd:commandline_handler',
    ]},
)

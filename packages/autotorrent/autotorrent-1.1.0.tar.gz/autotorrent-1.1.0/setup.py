#!/usr/bin/env python

from setuptools import setup

setup(
    name='autotorrent',
    version='1.1.0',
    description='AutoTorrent allows easy cross-seeding/', 
    author='Anders Jensen',
    author_email='johndoee+autotorrent@tidalstream.org',
    maintainer='John Doee',
    url='https://github.com/johndoee/',
    packages=['autotorrent'],
    install_requires=['BitTorrent-bencode'],
    license='BSD',
    entry_points={ 'console_scripts': [
        'autotorrent = autotorrent.cmd:commandline_handler',
    ]},
)

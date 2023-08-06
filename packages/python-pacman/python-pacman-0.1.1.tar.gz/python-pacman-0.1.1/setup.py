#!/usr/bin/env python

from distutils.core import setup

setup(
    name='python-pacman',
    version='0.1.1',
    description='Simple Python interface to Arch Linux package manager (pacman)',
    author='Jacob Cook',
    author_email='jacob@coderouge.co',
    url='https://git.coderouge.co/coderouge/python-pacman',
    py_modules=['pacman'],
    keywords = ['pacman', 'arch linux'],
    download_url = 'https://git.coderouge.co/coderouge/python-pacman/repository/archive.tar.gz?ref=0.1.1',
    license = 'GPLv3',
    classifiers = [
    	"Development Status :: 3 - Alpha",
    	"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    	"Operating System :: Unix",
    	"Topic :: System :: Software Distribution",
    ]
)

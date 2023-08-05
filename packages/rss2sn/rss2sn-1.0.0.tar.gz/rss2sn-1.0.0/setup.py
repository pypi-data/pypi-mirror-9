# -*- coding: utf-8 -*-
__version__ = "1.0.0"
import os
from distutils.core import setup

setup(
    name='rss2sn',
    version=__version__,
    url='http://git.tenak.net/?p=rss2sn.git',
    author='marc0s',
    author_email='marc0s@tenak.net',
    py_modules=['rss2sn'],
    install_requires=['StatusNet', ' feedparser', 'python-dateutil <= 1.5'],
    license='GPL3',
    description='A quick and dirty RSS to StatusNet bot',
    long_description=open('README.md').read(),
)


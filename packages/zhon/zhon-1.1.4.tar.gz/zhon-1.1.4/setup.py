#!/usr/bin/env python

import os
import sys

if sys.version_info < (3, ):
    import codecs
    enc_open = codecs.open
else:
    enc_open = open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with enc_open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='zhon',
    version='1.1.4',
    author='Thomas Roten',
    author_email='thomas@roten.us',
    url='https://github.com/tsroten/zhon',
    description=('Zhon provides constants used in Chinese text processing.'),
    long_description=long_description,
    packages=['zhon', 'zhon.cedict'],
    keywords=('chinese mandarin segmentation tokenization punctuation hanzi '
              'unicode radicals han cjk cedict cc-cedict traditional '
              'simplified characters pinyin zhuyin'),
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
    ],
    platforms='Any',
    test_suite='zhon.tests',
)

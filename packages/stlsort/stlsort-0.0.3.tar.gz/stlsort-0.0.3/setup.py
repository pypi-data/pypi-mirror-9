#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='stlsort',
    version='0.0.3',
    description='Sort ASCII STL files for better version control',
    long_description=''.join(open('README.rst').readlines()),
    keywords='STL, mesh, 3D, sort, git',
    author='nop head',
    author_email='nop.head@gmail.com',
    maintainer='Miro Hrončok',
    maintainer_email='miro@hroncok.cz',
    url='https://github.com/hroncok/stlsort',
    license='GPLv2',
    py_modules=['stlsort'],
    entry_points={'console_scripts': ['stlsort=stlsort:main']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from os.path import join

from setuptools import setup, find_packages
import pyyelp

# To get python setup.py test to work on python 2.7
try:
    import multiprocessing
    import logging
except ImportError:
    pass

setup(
    name=pyyelp.__name__,
    version=pyyelp.__version__,
    author=pyyelp.__author__,
    author_email=pyyelp.__email__,
    url='https://github.com/motte/python-yelp',
    download_url = 'https://github.com/motte/python-yelp/tarball/{0}'.format(pyyelp.__version__),
    description='Python wrapper for the Yelp v2 api',
    long_description=open('README.md').read(),
    license='ISC',
    packages = [pyyelp.__name__],
    keywords = ['yelp', 'wrapper', 'api'],
    install_requires=map(str.strip,open(join('requirements', 'base.txt'))),
    include_package_data=True,
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
    ),
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
setup.py

Created by Stephan Hügel on 2011-03-04
"""
import os
import re
import io
from setuptools import setup, find_packages

def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version=find_version("pyzotero/zotero.py")

setup(
    name='Pyzotero',
    version=version,
    description='Python wrapper for the Zotero API',
    author='Stephan Hügel',
    author_email='urschrei@gmail.com',
    license='GNU GPL Version 3',
    url='https://github.com/urschrei/pyzotero',
    include_package_data=True,
    download_url='https://github.com/urschrei/pyzotero/tarball/v%s' % version,
    keywords=['zotero'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    install_requires=['feedparser >= 5.1.0', 'pytz', 'requests'],
    extras_require={
        'ordereddict': ['ordereddict==1.1']
    },
    long_description="""\
A Python wrapper for the Zotero Server v3 API
---------------------------------------------

Provides methods for accessing Zotero Server API v3.
For full documentation see http://pyzotero.readthedocs.org/en/latest/

This version requires Python 2.7.x / 3.4.x"""
)

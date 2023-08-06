#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py file is part of pysed.

# Copyright 2014-2015 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# pysed is utility that parses and transforms text

# https://github.com/dslackw/pysed

# Pysed is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import gzip
import shutil

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pysed.__metadata__ import (
    __email__,
    __version__
)

setup(
    name="pysed",
    packages=['pysed'],
    scripts=["bin/pysed"],
    version=__version__,
    description="Utility that parses and transforms text",
    keywords=["python", "sed", "unix", "linux", "text",
                "stream", "editor"],
    author="dslackw",
    author_email=__email__,
    url="https://github.com/dslackw/pysed",
    package_data={"": ["LICENSE", "README.rst", "CHANGELOG"]},
    classifiers=[
        "Development Status :: 3 - Alpha"
        "Environment :: Console"
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        "Operating System :: Microsoft :: MS-DOS"
        "Operating System :: Microsoft :: Windows"
        "Operating System :: Microsoft :: Windows :: Windows 7"
        "Operating System :: Microsoft :: Windows :: Windows Vista"
        "Operating System :: Microsoft :: Windows :: Windows XP"
        "Operating System :: POSIX"
        "Operating System :: POSIX :: BSD :: BSD/OS"
        "Operating System :: POSIX :: BSD :: FreeBSD"
        "Operating System :: POSIX :: Linux"
        "Operating System :: POSIX :: Other"
        "Operating System :: Unix"
        "Programming Language :: Python"
        "Programming Language :: Python :: 2"
        "Programming Language :: Python :: 2.6"
        "Programming Language :: Python :: 2.7"
        "Programming Language :: Python :: 3"
        "Programming Language :: Python :: 3.0"
        "Programming Language :: Python :: 3.1"
        "Programming Language :: Python :: 3.2"
        "Programming Language :: Python :: 3.3"
        "Programming Language :: Python :: 3.4"
        "Topic :: Text Editors"
        "Topic :: Text Editors :: Documentation"
        "Topic :: Text Editors :: Text Processing"
        "Topic :: Text Editors :: Word Processors"
        "Topic :: Text Processing :: Filters"
        "Topic :: Text Processing :: General"
        "Topic :: Utilities"
        "Classifier: Topic :: Utilities"],
    long_description=open("README.rst").read()
)

if "install" in sys.argv:
    man_path = "/usr/man/man1/"
    if not os.path.exists(man_path):
        os.makedirs(man_path)
    man_page = "man/pysed.1"
    gzip_man = "man/pysed.1.gz"
    print("Installing '{0}' man page".format(gzip_man.split('/')[1]))
    f_in = open(man_page, "rb")
    f_out = gzip.open(gzip_man, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    shutil.copy2(gzip_man, man_path)

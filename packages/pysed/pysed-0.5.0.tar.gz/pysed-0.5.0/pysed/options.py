#!/usr/bin/env python
# -*- coding: utf-8 -*-

# main.py file is part of pysed.

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

import sys
from __metadata__ import (
    __prog__,
    __email__,
    __version__,
    __license__,
)


def usage():
    arguments = [
        "Usage: {0} [-h] [-v]".format(__prog__),
        "             [[-r] [-l] [-g] [-s] --write]"
    ]
    for arg in arguments:
        print("{0}".format(arg))


def helps():
    """print help"""
    arguments = [
        "{0} is utility that parses and transforms text\n".format(__prog__),
        "Usage: %s [OPTION] {pattern} {repl} {max} {flag} "
        "[input-file]\n" % (__prog__),
        "Options:",
        "  -h, --help                   display this help and exit",
        "  -v, --version                print program version and exit",
        "  -r, --replace                search and replace text",
        "  -l, --lines                  search pattern and print lines",
        "  -g, --highlight              highlight and print text",
        "  -s, --stat                   print text statics",
        "      --write                  write to file\n"
    ]
    for arg in arguments:
        print("{0}".format(arg))
    sys.exit()


def version():
    print('version : {0}'.format(__version__))
    print('License : {0}'.format(__license__))
    print('Email   : {0}'.format(__email__))
    sys.exit()

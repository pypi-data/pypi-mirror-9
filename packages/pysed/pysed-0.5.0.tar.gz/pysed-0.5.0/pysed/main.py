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

import re
import sys
from __metadata__ import __prog__
from options import (
    usage,
    helps,
    version
)


class Pysed(object):

    def __init__(self, args, data, filename, write):
        self.args = args
        self.flag = "0"
        self.count = 0
        self.write = write
        self.filename = filename
        if len(args) >= 2:
            self.pattern = args[1]
        if len(args) >= 3:
            self.repl = args[2]
        if len(args) >= 4:
            try:
                self.count = int(args[3])
            except ValueError:
                self.count = 0
        if len(args) > 5:
            self.flag = args[4]
        if len(self.args) > 6:
            self.write = args[6]
        self.color = ""
        self.color_def = "\x1b[0m"
        self.data = data.rstrip()
        self.text = ""

    def replaceText(self):
        """replace text with new"""
        self.regexFlags()
        self.text += re.sub(self.pattern, self.repl, self.data, self.count,
                            self.flag)
        self.selectPrintWrite()

    def findLines(self):
        """find text and print"""
        self.regexFlags()
        for line in self.data.splitlines():
            find = re.search(self.pattern, line, self.flag)
            if find:
                self.text += line + "\n"
        self.selectPrintWrite()

    def highLight(self):
        """highlight text and print"""
        self.colors()
        self.text = (self.data.replace(
            self.pattern, self.color + self.pattern + self.color_def))
        self.selectPrintWrite()

    def textStat(self):
        """print text statics"""
        lines, words = 0, 0
        chars = len(self.data.replace(" ", ""))
        blanks = len(self.data) - chars
        for line in self.data.splitlines():
            lines += 1
            words += len(re.findall(r"[\w']+", line))
        self.text = ("Lines: {0}, Words: {1}, Chars: {2}, Blanks: {3}".format(
            lines, words, chars, blanks))
        self.selectPrintWrite()

    def regexFlags(self):
        """python regex flags"""
        patt_flag = ""
        for i in self.flag.split("|"):
            re_patt = {
                "I": "2",
                "L": "4",
                "M": "8",
                "S": "16",
                "U": "32",
                "X": "64",
                "IGNORECASE": "2",
                "LOCALE": "4",
                "MULTILINE": "8",
                "DOTALL": "16",
                "UNICODE": "32",
                "VERBOSE": "64",
                "0": "0",
                "": ""
            }
            try:
                patt_flag += re_patt[i] + "|"
            except KeyError:
                usage()
                sys.exit("{0}: error: '{1}' flag doesn't exist".format(
                    __prog__, self.flag))
        if self.flag:
            self.flag = int(patt_flag[:-1])
        else:
            self.flag = 0

    def colors(self):
        """colors dict"""
        paint = {
            'black': '\x1b[30m',
            'red': '\x1b[31m',
            'green': '\x1b[32m',
            'yellow': '\x1b[33m',
            'blue': '\x1b[34m',
            'magenta': '\x1b[35m',
            'cyan': '\x1b[36m',
            }
        try:
            self.color = paint[self.repl]
        except KeyError:
            usage()
            sys.exit("{0}: error: '{1}' color doesn't exist".format(
                __prog__, self.repl))

    def selectPrintWrite(self):
        """write to file or print"""
        if self.write:
            self.writeFile(self.text)
        else:
            print(self.text.rstrip())

    def writeFile(self, newtext):
        """write data to file"""
        with open(self.filename, "w") as fo:
            for line in newtext.splitlines():
                fo.write(line + "\n")
            fo.close()


def execute(args, data, filename, isWrite):
    """execute available arguments"""
    if len(args) == 7 and args[6] not in ["-w", "--write"]:
        usage()
        sys.exit("{0}: error: '{1}' argument does not recognized".format(
            __prog__, args[6]))

    pysed = Pysed(args, data, filename, isWrite)
    if args[0] in ["-r", "--replace"]:
        pysed.replaceText()
    elif args[0] in ["-l", "--lines"]:
        pysed.findLines()
    elif args[0] in ["-g", "--highlight"]:
        pysed.highLight()
    elif args[0] in ["-s", "--stat"]:
        pysed.textStat()


def main():
    args = sys.argv
    args.pop(0)
    data = ""
    isWrite = False

    if len(args) == 1 and args[0] in ["-h", "--help"]:
        helps()
    elif len(args) == 1 and args[0] in ["-v", "--version"]:
        version()
    elif len(args) == 0:
        usage()
        sys.exit("{0}: error: Too few arguments".format(__prog__))
    elif args and args[0] not in ["-r", "--replace", "-l", "--lines",
                                  "-g", "--highlight", "-s", "--stat"]:
        usage()
        sys.exit("{0}: error: '{1}' argument does not recognized".format(
            __prog__, args[0]))

    if args[-1] in ["-w", "write"]:
        isWrite = True
        del args[-1]

    filename = "{0}.log".format(__prog__)
    not_piping = sys.stdin.isatty()
    if not_piping:
        fileInput = filename = args[len(args) - 1]
        try:
            f = open(fileInput)
            data = f.read()
        except IOError:
            usage()
            sys.exit("{0}: error: No such file or directory '{1}'".format(
                __prog__, args[len(args) - 1]))
    else:
        args.append("last")
        try:
            data = sys.stdin.read()
        except KeyboardInterrupt:
            print("")
            sys.exit()

    if len(args) > 7:
        usage()
        sys.exit("{0}: error: Too many arguments".format(__prog__))
    execute(args, data, filename, isWrite)

if __name__ == "__main__":
    main()

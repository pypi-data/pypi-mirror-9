.. image:: https://img.shields.io/github/release/dslackw/pysed.svg
    :target: https://github.com/dslackw/pysed/releases
.. image:: https://travis-ci.org/dslackw/pysed.svg?branch=master
    :target: https://travis-ci.org/dslackw/pysed
.. image:: https://landscape.io/github/dslackw/pysed/master/landscape.png
    :target: https://landscape.io/github/dslackw/pysed/master
.. image:: https://img.shields.io/codacy/5ef917a8c6354d8f9d984183c8fb5847.svg
    :target: https://www.codacy.com/public/dzlatanidis/pysed/dashboard
.. image:: https://img.shields.io/pypi/dm/pysed.svg
    :target: https://pypi.python.org/pypi/pysed
.. image:: https://img.shields.io/badge/license-GPLv3-blue.svg
    :target: https://github.com/dslackw/pysed
.. image:: https://img.shields.io/github/stars/dslackw/pysed.svg
    :target: https://github.com/dslackw/pysed
.. image:: https://img.shields.io/github/forks/dslackw/pysed.svg
    :target: https://github.com/dslackw/pysed
.. image:: https://img.shields.io/github/issues/dslackw/pysed.svg
    :target: https://github.com/dslackw/pysed/issues

.. contents:: Table of Contents:


About
=====

CLI utility that parses and transforms text written in Python.

Pysed is a Python stream editor, is used to perform basic text transformations
from a file. It reads text, line by line, from a file and replace, insert or print
all text or specific area. Actually pysed is a passage of Python module 're' in terminal.

Read more for `Regular Expression Syntax <https://docs.python.org/2/library/re.html>`_

`[CHANGELOG] <https://github.com/dslackw/pysed/blob/master/CHANGELOG>`_


Installation
------------

.. code-block:: bash

    $ pip install pysed --upgrade

    uninstall

    $ pip uninstall pysed
        


Command Line Tool Usage
-----------------------

.. code-block:: bash

    Usage: pysed [OPTION] {pattern} {repl} {max} {flag} [input-file]

    Options:
      -h, --help                   display this help and exit
      -v, --version                print program version and exit
      -r, --replace                search and replace text
      -l, --lines                  search pattern and print lines
      -g, --highlight              highlight and print text
      -s, --stat                   print text statistics
          --write                  write changes to file

Python regex flags
------------------

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Syntax	
     - Python syntax,	Meaning
   * - I or IGNORECASE	
     - re.IGNORECASE,	ignore case.
   * - M or MULTILINE	
     - re.MULTILINE,	make begin/end {^, $} consider each line.
   * - S or DOTALL	
     - re.DOTALL,	make . match newline too.
   * - U or UNICODE
     - re.UNICODE,	make {\w, \W, \b, \B} follow Unicode rules.
   * - L or LOCALE
     - re.LOCALE,	make {\w, \W, \b, \B} follow locale.
   * - X or VERBOSE	
     - re.VERBOSE,	allow comment in regex.

          
Usage Examples
--------------

.. code-block:: bash

    $ cat text.txt
    This is my cat,
     whose name is Betty.
    This is my dog,
     whose name is Frank.
    This is my fish,
     whose name is George.
    This is my goat,
     whose name is Adam.
    
    Replace text:

    $ pysed -r "name" "surname" text.txt
    This is my cat,
     whose surname is Betty.
    This is my dog,
     whose surname is Frank.
    This is my fish,
     whose surname is George.
    This is my goat,
     whose surname is Adam.

    Maximum replace text:
    
    $ pysed -r "name" "surname" 2 text.txt
    This is my cat,
     whose surname is Betty.
    This is my dog,
     whose surname is Frank.
    This is my fish,
     whose name is George.
    This is my goat,
     whose name is Adam.
     
    Add character to the beginning of each line:

    $ pysed -r "^" "# " 0 M text.txt
    # This is my cat,
    #  whose name is Betty.
    # This is my dog,
    #  whose name is Frank.
    # This is my fish,
    #  whose name is George.
    # This is my goat,
    #  whose name is Adam.
    
    Add character to the end of each line:
    
    $ pysed -r "$" " <-" 0 M text.txt
    This is my cat, <-
     whose name is Betty. <-
    This is my dog, <-
     whose name is Frank. <-
    This is my fish, <-
     whose name is George. <-
    This is my goat, <-
     whose name is Adam. <-

    Search and print lines:
    
    $ pysed -l "name" text.txt
     whose name is Betty.
     whose name is Frank.
     whose name is George.
     whose name is Adam.

    Highlight text:

    $ pysed -g "name" "red" text.txt
    This is my cat,
     whose name is Betty.
    This is my dog,
     whose name is Frank.
    This is my fish,
     whose name is George.
    This is my goat,
     whose name is Adam.

    Print statics text:

    $ pysed -s text.txt
    Lines: 8, Words: 32, Chars: 125, Blanks: 27

    Use the argument "--write" in any case when you want to save the changes like:
    
    $ pysed -r "name" "surname" text.txt --write

    
    Use as piping:

    $ echo "This is my cat, whose name is Betty" | pysed -r "cat" "dog"
    This is my dog, whose name is Betty

    $ echo "This is my cat, whose name is Betty" | pysed -r "[^\W]+" "-"
    - - - -, - - - -
    
    $ echo "This is my cat, whose name is Betty" | pysed -r "is" "IS" 1
    ThIS is my cat, whose name is Betty

    $ echo "910a13de57dfbdf6f06675db975f8407" | pysed -r "[^\d+]" ""
    91013576066759758407

    $ echo "/usr/local/bin" | pysed -r "/local" ""
    /usr/bin

Please report `Issues <https://github.com/dslackw/pysed/issues>`_

Copyright 
---------

- Copyright © Dimitris Zlatanidis
- Linux is a Registered Trademark of Linus Torvalds.

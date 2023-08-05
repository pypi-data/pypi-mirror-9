#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from isbntools.app import quiet_errors, EAN13


def usage():
    print('Usage: isbn_EAN13 ISBN')


def main():
    sys.excepthook = quiet_errors
    try:
        print(EAN13(sys.argv[1]))
    except:
        usage()

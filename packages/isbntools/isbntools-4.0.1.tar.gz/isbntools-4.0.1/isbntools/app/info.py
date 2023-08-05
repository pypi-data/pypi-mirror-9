#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from isbntools import info


def usage():
    print('Usage: isbn_info ISBN')
    sys.exit(1)


def main():
    try:
        print((info(sys.argv[1])))
    except:
        usage()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import logging

from tcflib.service import Read
from tcflib.tcf import serialize
from tcfnetworks.annotators.cooccurrence import CooccurrenceWorker


def test():
    result = Read('tcf04-karin-wl.xml') | CooccurrenceWorker(method='window')
    print(serialize(result))
    result = Read('tcf04-karin-wl.xml') \
            | CooccurrenceWorker(method='window', spantype='paragraph')
    result = Read('tcf04-karin-wl.xml') \
            | CooccurrenceWorker(method='sentence')
    result = Read('tcf04-karin-wl.xml') \
            | CooccurrenceWorker(method='textspan', spantype='paragraph')
    result = Read('tcf04-karin-wl.xml') \
            | CooccurrenceWorker(method='sentence_window', window=[2])

def main():
    # Parse commandline arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-o', '--outfile', default=sys.stdout,
                            type=argparse.FileType('w'))
    args = arg_parser.parse_args()
    # Set up logging
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.ERROR
    logging.basicConfig(level=level)
    # Return exit value
    return test()


if __name__ == '__main__':
    sys.exit(main())

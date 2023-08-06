#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
output columns of various CSV files

Example::

> cat-columns foo.csv:0 bar.csv:1,2,3 fleem.csv

This will generate CSV output with the first column from `foo.csv`,
the 2nd, 3rd, and 4th columns from `bar.csv`,
and all columns from `fleem.csv`.
"""

# imports
import argparse
import csv
import os
import sys
import time
from collections import OrderedDict
from .read import read_csv

# module globals
__all__ = ['cat_columns', 'CatColumnParser', 'main']

def cat_columns(csv_files):
    """
    csv_files -- an iterable of 2-tuples of `path`, columns
    """

    rows = []

class CatColumnParser(argparse.ArgumentParser):
    """CLI option parser"""
    def __init__(self, **kwargs):
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('csv', nargs='+',
                          help="path to CSV files and columns to output, delimited by ':' and comma-separated")
        self.add_argument('-o', '--output', dest='output',
                          type=argparse.FileType('a'), default=sys.stdout,
                          help="where to output to, or stdout by default")
        self.options = None

    def parse_args(self, *args, **kw):
        options = argparse.ArgumentParser.parse_args(self, *args, **kw)
        self.validate(options)
        self.options = options
        return options

    def validate(self, options):
        """validate options"""

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = CatColumnParser()
    options = parser.parse_args(args)

    # get the data
    csv_files = OrderedDict()
    missing = []
    for item in options.csv:
        if ':' in item:
            path, columns = item.rsplit(':', 1)
            columns = columns.strip()
            if columns:
                columns = [int(column) for column in columns.split(',')]
            else:
                columns = None
        else:
            path = item
            columns = None
        if not os.path.exists(path):
            missing.append(path)
    if missing:
        parser.error("File(s) not found:\n{}".format('\n'.join(missing)))

    # concatenate the rows
    data = cat_columns(csv_files.items())

    # output it
    writer = csv.writer(options.output)
    for row in data:
        writer.write_row(row)
        options.output.flush()

if __name__ == '__main__':
    main()



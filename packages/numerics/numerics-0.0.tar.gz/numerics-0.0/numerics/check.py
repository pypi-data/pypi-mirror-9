#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data integrity checking
"""

# imports
import argparse
import os
import subprocess
import sys

# module globals
__all__ = ['main', 'CheckParser']
string = (str, unicode)

class NumberOfColumnsException(Exception):
    """wrong number of columns"""

def check_column_lengths(*rows):
    """ensure all column lengths are the same and return number"""
    lengths = set([len(row) for row in rows])
    if len(lengths) > 1:
        raise NumberOfColumnsException("Multiple numbers of columns: {}".format(', '.join(lengths)))
    return lengths.pop()


class CheckParser(argparse.ArgumentParser):
    """CLI option parser"""
    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
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
    parser = Parser()
    options = parser.parse_args(args)

if __name__ == '__main__':
    main()


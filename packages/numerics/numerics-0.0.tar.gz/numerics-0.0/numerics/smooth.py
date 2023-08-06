#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
smoothing
"""

# imports
import argparse
import os
import subprocess
import sys

# module globals
__all__ = ['main', 'smooth', 'SmoothingParser']

def smooth(iterations, *values):
    assert len(values) >= 2
    while iterations > 0:
        inner = [sum(i) for i in zip(values[1:], values[:-1])]
        left = [inner[0]] + inner[:]
        right = inner[:] + [inner[-1]]
        values = [0.25*sum(i) for i in zip(left, right)]
        iterations -= 1
    return values

class SmoothingParser(argparse.ArgumentParser):
    """`smooth` CLI option parser"""
    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('input', nargs='?',
                          type=argparse.FileType('r'), default=sys.stdin,
                          help='input file, or read from stdin if ommitted')
        self.add_argument('-o', '--output', dest='output',
                          type=argparse.FileType('a'), default=sys.stdout,
                          help="output file to write to, or stdout")
        self.add_argument('-n', '--iterations', dest='iterations',
                          type=int, default=1,
                          help="number of iterations to apply [DEFAULT: %(default)s]")
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
    parser = SmoothingParser()
    options = parser.parse_args(args)

    # read data
    data = options.input.read().strip().split()
    data = [float(i) for i in data]

    smoothed = smooth(options.iterations, *data)

    # write data
    options.output.write('\n'.join([str(i) for i in smoothed]))

if __name__ == '__main__':
    main()


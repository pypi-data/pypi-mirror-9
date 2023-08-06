#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
text display
"""

# imports
import argparse
import sys
from collections import OrderedDict
from math import floor

# module globals
__all__ = ['main', 'blocks', 'frac', 'FracParser']

# Unicode is awesome; see http://www.alanwood.net/unicode/block_elements.html
blocks = OrderedDict([(0.,    ''),
                      (0.125, '▏'),
                      (0.25,  '▎'),
                      (0.375, '▍'),
                      (0.5,   '▌'),
                      (0.625, '▋'),
                      (0.75,  '▊'),
                      (0.875, '▉'),
                      (1.,    '█'),
                  ])


def iterable(obj):
    """is `obj` iterable?"""
    # TODO: should probably go elsewhere
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def frac(fractions, width=20, bar=''):
    """display fractions"""
    if not iterable(fractions):
        # convert single item to list
        fractions = [fractions]
    retval = []
    for fraction in fractions:
        whole = int(floor(fraction*width))
        part = (fraction*width)-whole
        line = blocks[1.]*whole + blocks[int(floor(part * 8))/8.]
        retval.append(line)
    if bar:
        lines = []
        for line in retval:
            newline = "{bar}{}{bar}".format(line.ljust(width),
                                            bar=bar)
            lines.append(newline)
        retval = lines
    return retval


class FracParser(argparse.ArgumentParser):
    """CLI option parser"""
    def __init__(self, **kwargs):
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('fraction', type=float, nargs='+',
                          help="fractions to display")
        self.add_argument('-w', '--width', dest='width',
                          type=int, default=40,
                          help="width to display [DEFAULT: %(default)s]")
        self.options = None

    def parse_args(self, *args, **kw):
        options = argparse.ArgumentParser.parse_args(self, *args, **kw)
        self.validate(options)
        self.options = options
        return options

    def validate(self, options):
        """validate options"""
        if options.width < 1:
            self.error("Width must be greater than zero (You gave: {})".format(options.width))
        out_of_range = [i for i in options.fraction
                        if not (0. <= i <= 1.)]
        if out_of_range:
            self.error("Fractions should be between 0 and 1")

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = FracParser()
    options = parser.parse_args(args)

    # get fractions display
    lines = frac(options.fraction, width=options.width)

    # display
    print ('\n'.join(lines))

if __name__ == '__main__':
    main()



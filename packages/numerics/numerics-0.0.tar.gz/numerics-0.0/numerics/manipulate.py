#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
manipulate CSV data
"""

# imports
import argparse
import os
import sys
from .convert import default_cast, cast_columns
from .data import transpose
from .read import CSVParser
from .sort import Sorter, sort_arg

# module globals
__all__ = ['ManipulationParser', 'FloatParser', 'main']


class ManipulationParser(CSVParser):
    """CLI option parser for data manipulation"""

    types = default_cast

    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        CSVParser.__init__(self, **kwargs)
        self.add_argument('--sort', dest='sort', nargs='+',
                          type=sort_arg,
                          help="column to sort by; will be reverse if prepended by '-'")
        self.options = None

    def typed_data(self):
        """return parsed and casted data"""
        columns = cast_columns(self.columns(), self.types)

        if self.options.sort:
            # sort the data
            sorter = Sorter(*self.options.sort)
            rows = sorter(transpose(columns))

            # re-transpose
            columns = transpose(rows)

        return columns

    def process(self):
        return transpose(self.typed_data())


class FloatParser(ManipulationParser):
    """manipulation parser convenience just for floats"""
    types = (float,)


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = ManipulationParser()
    options = parser.parse_args(args)

    # write manipulated data
    parser.write(parser.process())

if __name__ == '__main__':
    main()

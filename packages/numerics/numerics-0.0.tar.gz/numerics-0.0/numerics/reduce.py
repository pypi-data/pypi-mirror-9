#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reduce a vector to a scalar
"""

# imports
import sys
from .filters import mean
from .manipulate import FloatParser
from .write import CSVWriter

# module globals
__all__ = ['ReduceParser']


class ReduceParser(FloatParser):
    """CLI option parser"""

    def __init__(self, function, **kwargs):
        """
        function -- reducing function
        """

        self.function = function
        kwargs.setdefault('description', __doc__)
        FloatParser.__init__(self, **kwargs)

    def __call__(self, *args):

        # parse command line options
        self.parse_args(args or sys.argv[1:])

        # read data
        columns = self.typed_data()
        if not columns:
            self.error("No data given")

        # calculate scalars
        data = [self.function(column) for column in columns]

        # write CSV
        writer = CSVWriter(self.options.output)
        writer.write([data])

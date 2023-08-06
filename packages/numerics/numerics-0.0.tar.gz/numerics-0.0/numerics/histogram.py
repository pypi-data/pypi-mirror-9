#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Histograms
"""

# imports
import argparse
import os
import sys
import time
from .data import transpose
from .generate import frange
from .read import CSVParser
from .write import CSVWriter
from collections import OrderedDict

# module globals
__all__ = ['Histogram', 'HistogramParser', 'main']

class Histogram(object):
    """historgram"""

    def __init__(self, bins):
        self.bins = sorted(bins)
        assert len(bins) > 1
        self.data = OrderedDict([(bin, [])
                                 for bin in zip(bins[:-1],
                                                bins[1:])])

    def add(self, *values):
        """add values to the histogram"""
        for value in values:
            for vmin, vmax in self.data.keys():
                if vmin <= value < vmax:
                    self.data[(vmin, vmax)].append(value)
                    break
            else:
                if value == vmax:
                    # handle rightmost endpoint
                    self.data[(vmin, vmax)].append(value)

    def __iadd__(self, value):
        self.add(value)
        return self

    def __call__(self, *values):
        """
        add values to the histogram and return
        OrderedDict of counts
        """
        self.add(*values)
        return OrderedDict([(bin, len(value))
                            for bin, value in self.data.items()])

    def keys(self):
        return self.data.keys()

    def max(self):
        """return max length"""
        return max([len(value) for value in self.data.values()])


class HistogramParser(CSVParser):
    """histogram CLI option parser"""

    def __init__(self, **kwargs):
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        kwargs.setdefault('description', __doc__)
        CSVParser.__init__(self, **kwargs)
        self.add_argument('-n', '--bins', dest='n_bins', type=int,
                          help="number of bins")
        self.add_argument('--min', dest='min', type=float,
                          help="minimum value; else taken from data")
        self.add_argument('--max', dest='max', type=float,
                          help="maximum value, else taken from data")
        self.options = None


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = HistogramParser()
    options = parser.parse_args(args)

    # read data
    data = parser.read()
    if not data:
        parser.error("No data given")

    # transpose to columns
    columns = transpose(data)

    # cast to float
    columns = [[float(value) for value in column]
               for column in columns]

    # find min, max if not provided
    if options.min is None:
        options.min = min([min(column) for column in columns])
    if options.max is None:
        options.max = max([max(column) for column in columns])

    if not options.n_bins:
        # find number of bins, if not specified
        # We'll use a guess of 2 items per bin, on average
        options.n_bins = len(columns[0]) / 2

    # make some bins
    bins = frange(options.min, options.max, options.n_bins)

    # make some histograms
    histograms = []
    for column in columns:
        histogram = Histogram(bins)
        histogram.add(*column)
        histograms.append(histogram)

    # record delimeters for output
    columns = zip(*histograms[0].keys())
    for histogram in histograms:
        columns.append(histogram().values())

    # transpose back to rows
    rows = transpose(columns)

    # output
    writer = CSVWriter(options.output)
    writer.write(rows)

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
plot data with `matplotlib`

See also :
- http://stackoverflow.com/questions/7534453/matplotlib-does-not-show-my-drawings-although-i-call-pyplot-show ;
- http://bokeh.pydata.org/ ;
- http://mpld3.github.io/

For bokeh tools...
https://github.com/bokeh/bokeh/blob/master/bokeh/plotting_helpers.py#L277
"""

# imports
import argparse
import csv
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from .manipulate import ManipulationParser

# module globals
__all__ = ['Plot', 'PlotParser', 'read', 'main']
string = (str, unicode)


class Plot(object):
    """plotting class"""
    def __init__(self, title=None, xlabel=None, ylabel=None):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self._x = None
        self._y = []
        self.marker = []

    def x(self, data, label=None):
        self._x = data
        if label is not None:
            self.xlabel = xlabel

    def y(self, data, label=None, marker='.'):
        self._y.append(data)
        self.marker.append(marker)
        if label is not None:
            self.ylabel = label

    def __call__(self, output):
        assert self._y

        if self.title:
            plt.title(self.title)
        if self.xlabel:
            plt.xlabel(self.xlabel)
        if self.ylabel:
            plt.ylabel(self.ylabel)
        if self._x:
            args = sum([[self._x, self._y[i], self.marker[i]] for i in range(len(self._y))], [])
            plt.plot(*args)
        else:
            plt.plot(*self._y)
        plt.show()
        plt.savefig(output)
        print ("{}->saved to '{}'".format(self.title or '', output))


def read(f):
    """
    Read from file ``f``
    Accepts CSV and space-delimited files
    """

    retval = None
    for line in f:
        line = line.strip()
        if ',' in line:
            buffer = StringIO()
            buffer.write(line)
            buffer.seek(0)
            row = list(csv.reader(buffer))[0]
        else:
            row = line.split()
        row = [float(i) for i in row]
        if retval is None:
            retval = [[i] for i in row]
        else:
            for index, value in enumerate(row):
                retval[index].append(value)

    return retval


class PlotParser(ManipulationParser):
    """CLI option parser for the plotter"""

    types = (float,)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('description', __doc__)
        ManipulationParser.__init__(self, *args, **kwargs)
        self.add_argument('-s', '--scatter', dest='scatter',
                          action='store_true', default=False,
                          help="scatter plot")
        self.options = None
        self.set_defaults(output=None)


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = PlotParser()
    options = parser.parse_args(args)

    # choose plotting function
    plot_fcn = plt.scatter if options.scatter else plt.plot

    # read data
    all_data = [read(open(f)) # quick hack
                for f in options.input]

    # color map
    # http://stackoverflow.com/questions/12236566/setting-different-color-for-each-series-in-scatter-plot-on-matplotlib
    n_col = sum([(len(data)-1) or 1 for data in all_data])
    colors = iter(cm.rainbow(np.linspace(0, 1, n_col)))

    for data in all_data:
        # plot each data set
        if len(data) == 1:
            plot_fcn(*data, marker='.', color=next(colors))
        else:
            for i in range(1, len(data)):
                plot_fcn(data[0], data[i], label=str(i), marker='.', color=next(colors))

    # save plot
    if options.output:
        plt.savefig(options.output)
        print ("Figure saved to file://{}".format(os.path.abspath(options.output)))

    # display plot, I guess
    plt.show()

if __name__ == '__main__':
    main()

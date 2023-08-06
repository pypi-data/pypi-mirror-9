#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
bar charts using bokeh

See:
- http://bokeh.pydata.org/tutorial/solutions/gallery/olympics.html
"""

# imports
import argparse
import sys
import tempfile
from .data import transpose
from .manipulate import ManipulationParser
#from bokeh.charts import Bar
#from bokeh.plotting import *
from bokeh.plotting import figure, output_file, show, VBox
from collections import OrderedDict

__all__ = ['bar_chart', 'BarChartParser', 'main']


def bar_chart(data, output, title=None):
    """
    create a bar chart

    See:
    - http://bokeh.pydata.org/en/latest/tutorial/solutions/gallery/olympics.html
    """
    # TODO:  abstract this to a plot class


    # create a figure
    p1 = figure(title=title,
                tools="pan,wheel_zoom,box_zoom,reset,resize",
                x_range=data[0]
            )
    if not len(data) == 2:
        raise NotImplementedError('TODO') # -> record TODO items

    p1.rect(x=data[0], y=data[1], height=data[1], width=0.2)
    show(VBox(p1))

#    bar = Bar(data, tools="pan,wheel_zoom,box_zoom,reset,resize")
#    bar.filename(output)
#    bar.width(len(data)*50)
#    bar.show()


class BarChartParser(ManipulationParser):
    """command line options parser for bar charts"""
    # TODO: upstream to PlotParser

    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        ManipulationParser.__init__(self, **kwargs)
        self.add_argument('-t', '--title', dest='title',
                          help="plot title")

    def plot_filename(self):
        """determine the plot filename"""
        # this is a STUB
        # in reality, this should come from -o, --output
        # if applicable, or, should be determined from
        # the plot --title, or should be eg
        # '20150315203424.html'
        # we are doing this right nowe to work around the fact
        # that bokeh, in particular, will just cry if you
        # don't set this
        return 'foo.html'


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = BarChartParser()
    options = parser.parse_args(args)

    # process data
    data = parser.typed_data()

    # ensure a mapping is given
    if len(data) == 1:
        data.insert(0, range(len(data[-1])))
    if len(data) != 2:
        parser.error("A mapping is required")
#    mapping = OrderedDict(transpose(data))


    # generate bar chart
    bar_chart(data, parser.plot_filename(), title=options.title)
#    bar_chart(data, options.output, title=options.title)

# BBB keeping this around for reference;
# we should probably move to a better parsing system at some point
# parse file
#    data = pd.read_csv(options.input, header=None, names=options.columns, index_col=0)

if __name__ == '__main__':
    main()

#!/usr/bin/env python

"""
interpolation
"""

# imports
import argparse
import sys

__all__ = ['neighbors', 'linear_interpolation', 'InterpolateParser']

def neighbors(start, finish):
    """
    returns the neighbors in finish from start
    assumes both are sorted
    """
    assert finish
    index = 0
    retval = []
    for x in start:
        # endpoints
        if x < finish[0]:
            retval.append((None, 0))
            continue
        if x > finish[-1]:
            retval.append((len(finish)-1, None))
            continue
        # traverse
        try:
            while True:
                if x < finish[index] or x > finish[index+1]:
                    index += 1
                    continue
                else:
                    break
            retval.append((index, index+1))
        except IndexError:
            retval.append((len(finish)-2, len(finish)-1))

    return retval


def linear_interpolation(data, points):
    """
    linearly interpolate data to points

    data -- iterable of 2-tuples (or equivalent) of `x,y`
    points -- `x`-values to interpolate to
    """

    # ensure we are sorted
    data = sorted(data, key=lambda x: x[0])
    points = sorted(points)

    # get the neighbors
    x = [value[0] for value in data]
    nearest_neighbors = neighbors(points, x)

    # we don't support endpoints yet; this is interpolation, not extrapolation
    if any([(neighbor[0] is None or neighbor[1] is None)
            for neighbor in nearest_neighbors]):
        raise AssertionError("Bad neighbors: {}".format(nearest_neighbors))

    retval = []
    for index, (left, right) in enumerate(nearest_neighbors):
        # linearly interpolate
        ratio = (points[index] - data[left][0])/float(data[right][0] - data[left][0])
        retval.append(ratio*data[right][1] + (1.-ratio)*data[left][1])
    return retval

class InterpolateParser(argparse.ArgumentParser):
    """CLI option parser"""

    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('input', nargs='?',
                          type=argparse.FileType('r'), default=sys.stdin,
                          help='input file, or read from stdin if ommitted')
        self.add_argument('-o', '--output', dest='output',
                          type=argparse.FileType('w'), default=sys.stdout,
                          help="output file, or stdout if ommitted")
        self.add_argument('--points', '--print-points', dest='print_points',
                          action='store_true', default=False,
                          help="print the points to interpolate to and exit")
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
    parser = InterpolateParser()
    options = parser.parse_args(args)

    # read the CSV
    reader = csv.reader(options.input)
    data = [[float(col) for col in row] for row in reader]
    ncols = set([len(row) for row in data])
    assert len(ncols) == 1
    ncols = ncols.pop()
    assert ncols > 1

    # get `x` values
    data = sorted(data, key=lambda x: x[0])
    x = [row[0] for row in data]
    xmin = int(x[0]) + 1
    xmax = int(x[-1])
    points = range(xmin, xmax+1)
    if options.print_points:
        print ('\n'.join([str(point) for point in points]))
        return

    # make into x,y series
    series = [[(row[0], row[col]) for row in data]
              for col in range(1,ncols)]

    # interpolate
    interpolated = [linear_interpolation(s, points) for s in series]

    # output interpolated data
    writer = csv.writer(options.output)
    for row in zip(points, *interpolated):
        writer.writerow(row)

if __name__ == '__main__':
    main()

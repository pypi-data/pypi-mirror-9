#!/usr/bin/env python

"""
convert between types
"""

# imports
import argparse
import csv
import sys
from .data import transpose
from .read import read_csv, CSVParser

__all__ = ['default_cast',
           'cast',
           'float_or_orig',
           'main']

default_cast = (int, float, str)

def cast(to_type, *values):
    """
    gently cast a thing to a thing;
    if you can't, return the original value
    """


    retval = []
    for value in values:
        try:
            retval.append(to_type(value))
        except ValueError:
            retval.append(value)
    return retval

def cast_or_discard(to_type, *values):
    """
    cast to `to_type` if possible;
    otherwise just throw away
    """
    retval = []
    for value in values:
        try:
            retval.append(to_type(value))
        except ValueError:
            continue
    return retval


def float_or_orig(*values):
    return cast(float, *values)
    # convenience function ; do we need this?


def column_type(values, types=default_cast):
    """determine the type of a column"""
    for t in types:
        for value in values:
            try:
                t(value)
            except ValueError, TypeError:
                break
        else:
            return t


def cast_columns(columns, types=default_cast):
    """
    cast a column of data
    """
    column_types = [column_type(column, types=types)
                    for column in columns]
    return [[_type(row) for row in column]
            for _type, column in zip(column_types, columns)]


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = CSVParser(description="interpolate types from file")
    options = parser.parse_args(args)

    # read CSV file columns
    columns = parser.columns()

    # get types
    types = [column_type(column) for column in columns]

    # print type information
    writer = csv.writer(sys.stdout)
    writer.writerow([t.__name__ for t in types])


if __name__ == '__main__':
    main()

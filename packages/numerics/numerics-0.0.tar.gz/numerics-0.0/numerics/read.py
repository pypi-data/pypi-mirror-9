#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
read CSV
"""
# TODO: support other formats


# imports
import argparse
import csv
import os
import sys
from .data import transpose
from .write import CSVWriter

# module globals
__all__ = ['CSVSchema', 'read_csv', 'CSVParser', 'main']
string = (str, unicode)


class CSVSchema(object):
    """read CSV with a schema"""

    def __init__(self, columns):
        self.columns = columns

    def read(self, f):

        if isinstance(f, string):
            with open(f) as fp:
                return self.read(fp)

        retval = []
        reader = csv.reader(f)
        for row in reader:
            retval.append(dict(zip(self.columns, row)))
        return retval

    __call__ = read


def aggregate_columns(directory, schema):

    # check for missing files
    missing = [path for path in schema
               if not os.path.exists(os.path.join(directory, path))]
    assert not missing, "Missing files: {}".format(', '.join(missing))

    # read records
    records = {filename: CSVSchema(columns).read(os.path.join(directory, filename))
               for filename, columns in schema.items()}


    # check lengths
    lengths = [len(value) for value in records.values()]
    assert len(set(lengths)) == 1, "Differing lengths found for files"

    # build new rows
    retval = []
    for row in zip(*records.values()):
        new_row = {}
        for record in row:
            for key, value in record.items():
                if new_row.get(key, value) != value:
                    raise AssertionError("{} != {}".format(new_row.get(key), value))
                new_row[key] = value
        retval.append(new_row)

    return retval


def read_csv(*fp):
    """read a series of CSV files"""

    retval = []
    for f in fp:

        if isinstance(f, string):
            with open(f) as _f:
                retval.extend(read_csv(_f))
            continue

        reader = csv.reader(f)
        retval.extend([row for row in reader])

    return retval


class CSVParser(argparse.ArgumentParser):
    """CLI option parser"""

    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('input', nargs='*',
                          help="CSV input files to read, or read from stdin")
        self.add_argument('-+', '--add', dest='added_columns', nargs='+',
                          help="append this column")
        self.add_argument('-c', '--col', '--columns', dest='columns',
                          nargs='+', type=int,
                          help="column numbers to output, starting with 0")
        self.add_argument('-o', '--output', dest='output',
                          type=argparse.FileType('a'), default=sys.stdout,
                          help='output destination, or stdout')
        self.add_argument('--index', dest='index',
                          action='store_true', default=False,
                          help="prepend each row with numeric index")
        self.options = None

    def parse_args(self, *args, **kw):
        options = argparse.ArgumentParser.parse_args(self, *args, **kw)
        self.validate(options)
        self.options = options
        return options

    def validate(self, options):
        """validate options"""
        options.input = options.input or [sys.stdin]

    def read(self):
        """read and process CSV"""

        data = read_csv(*self.options.input)

        if self.options.added_columns:
            # add columns
            for row in data:
                row.extend(options.added_columns)

        if self.options.columns:
            # filter by column
            data = [[row[column] for column in self.options.columns]
                    for row in data]

        if self.options.index:
            # prepend numeric index
            for index, row in enumerate(data):
                row.insert(0, index)

        # return processed data
        return data

    def columns(self):
        """return columns vs `data`'s rows"""
        return transpose(self.read())

    def write(self, data):
        """write data to specified CSV destination"""
        # TODO: support more formats
        CSVWriter(self.options.output).write(data)

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = CSVParser()
    parser.add_argument('--transpose', dest='transpose',
                        action='store_true', default=False,
                        help="transpose columns and rows")
    options = parser.parse_args(args)

    # read CSV
    if options.transpose:
        data = parser.columns()
    else:
        data = parser.read()

    # write CSV
    parser.write(data)

if __name__ == '__main__':
    main()


# -*- coding: utf-8 -*-

"""
data models
"""

from collections import OrderedDict

__all__ = ['ColumnNumberException',
           'ColumnLengthException',
           'transpose',
           'Rows',
           'Columns']


class ColumnNumberException(Exception):
    """
    wrong number of columns: {given} given; {expected} expected
    """
    def __init__(self, given, expected):
        self.given = given
        self.expected = expected
        Exception.__init__(self.__doc__.format(**self.__dict__).strip())


def transpose(array):
    """makes rows into columns or vice versa"""

    if not array:
        return array  # nothing to do

    n_cols = set([len(row) for row in array])
    if len(n_cols) != 1:
        raise Exception("Differing number of columns found: {}".format(', '.join(sorted(n_cols))))

    return zip(*array)


class ColumnLengthException(ColumnNumberException):
    """
    wrong length of column: {given} given; {expected} expected
    """
    # XXX should share ABC, not inherit from ColumnNumberException


class Rows(object):
    """
    row-based data
    """

    array = OrderedDict

    def __init__(self, columns, *rows):
        """
        columns -- column labels
        """
        self.column_names = columns
        self.rows = []

        for row in rows:
            self += row

    def __iadd__(self, row):
        """add a labeled row"""
        if len(row) != len(self.columns_names):
            raise ColumnNumberException(len(row), len(self.columns_names))
        self.rows.append(self.array(zip(self.columns_names, row)))

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, item):
        return self.rows[item]


class Columns(object):
    """
    column-oriented data
    """

    def __init__(self, *columns):
        self.columns = OrderedDict()  # this should be ordered
        for name, values in columns:
            self += (name, values)

    def __iadd__(self, item):
        column_name, values = item
        assert column_name not in self.columns
        return self

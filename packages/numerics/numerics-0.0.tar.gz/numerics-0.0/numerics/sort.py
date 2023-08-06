#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
sort columned data
"""

# module globals
__all__ = ['sort_arg', 'Sorter']

def sort_arg(string):
    """converter appropriate for command line argument conversion"""

    forward = True
    if string.startswith('-'):
        forward = False
        string = string[1:]
    return (int(string), forward)


class Sorter(object):
    """
    sorter for columned data
    """

    def __init__(self, *indices):
        """
        indices -- 2-tuple of (index, forward)
        where forward should be True or False
        """
        self.indices = indices

    def __call__(self, rows):
        return sorted(rows, key=self.key)

    def key(self, row):
        retval = []
        for index, forward in self.indices:
            value = row[index]
            if not forward:
                value = -value
            retval.append(value)
        return tuple(retval)

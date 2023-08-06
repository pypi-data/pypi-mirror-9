#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
string = (str, unicode)
__all__ = ['CSVWriter']

class CSVWriter(object):
    """a more sensible front-end to writing CSV files"""

    def __init__(self, f, mode='a'):
        if isinstance(f, string):
            f = open(f, mode)
        self.f = f
        self.writer = csv.writer(f)

    def __call__(self, *data):
        self.writer.writerow(data)
        self.f.flush()

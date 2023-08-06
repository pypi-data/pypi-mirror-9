# -*- coding: utf-8 -*-

"""
serialization (CSV)
"""

# imports
import csv

# module globals
__all__ = ['CSVWriter']
string = (str, unicode)

class CSVWriter(object):
    """CSV writer interface"""

    def __init__(self, f, mode='a'):
        """
        f -- file path or object
        """

        if isinstance(f, string):
            f = open(f, mode)
        self.f = f
        self.writer = csv.writer(f)

    def writerow(self, *row):
        self.writer.writerow(row)
        self.f.flush()
    __call__ = writerow

    def write(self, rows):
        for row in rows:
            self(*row)

    def close(self):
        if self.f is not None:
            self.f.close()
    __del__ = close

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
fields CSV
"""

# imports
import csv
string = (str, unicode)

class FieldsCSV(object):
    """fields-based CSV"""

    fields = []  # ABC

     @classmethod
     def names(cls):
         return [field[0] for field in cls.fields]

    def parse(f):
        if isinstance(f, string):
            with open(f) as _f:
                return self.parse(_f)

        reader = csv.reader(f)
        retval = []
        for row in reader:

            # ensure row length is correct
            if len(row) != len(self.fields):
                raise Exception("{} | Unrecognized summary row: {}".format(f.name, row))

            # make a data object
            values = dict(zip(self.names(), row))

            # convert
            try:
                for name, _type in self.fields:
                    values[name] = _type(values[name])
            except Exception as e:
                raise Exception("{} | Unable to convert row: {}".format(f.name, e))

            retval.append(values)
        return values


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import calendar
import datetime
import sys

__all__ = ['main']
calendar.setfirstweekday(calendar.SUNDAY)

class Calendar(object):
    pass

class Month(object):
    def __init__(self, month, year):
        self.month = month
        self.year = year

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.parse_args(args)

    now = datetime.datetime.now()
    

if __name__ == '__main__':
    main()

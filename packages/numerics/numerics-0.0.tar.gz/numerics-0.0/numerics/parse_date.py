#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
parse date
"""

import argparse
import datetime
import sys
import time
from .formatting import format_table
from dateutil.parser import parse

__all__ = ['main', 'parse_date', 'epoch2local', 'epoch2utc', 'is_dst', 'timezone']

def is_dst(localtime=None):
    """returns if daylight savings time is in effect locally"""
    return time.localtime(localtime).tm_isdst > 0

def timezone(localtime=None):
    """returns name of local timezone"""
    return time.tzname[int(is_dst(localtime))]

def epoch2local(datestamp):
    """convert epoch to local time"""
    return datetime.datetime.fromtimestamp(float(datestamp))

def epoch2utc(datestamp):
    """convert epoch to UTC"""
    return datetime.datetime.utcfromtimestamp(float(datestamp))


def parse_date(datestamp):
    """returns seconds since epoch from the supplied date"""

    try:
        # already epoch timestamp
        return float(datestamp)
    except ValueError:
        pass

    # parse the string
    parsed_date = parse(datestamp)

    # convert this to seconds since epoch
    return time.mktime(parsed_date.timetuple())


def main(args=sys.argv[1:]):

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('date', nargs='+',
                        help="local date to parse")
    options = parser.parse_args(args)

    # parse each date
    epochs = [parse_date(d) for d in options.date]

    # display results
    header = ['epoch', 'local', 'UTC']
    print (format_table([[d, '{} {}'.format(epoch2local(d), timezone(d)), epoch2utc(d)] for d in epochs],
                        header=header, joiner='|'))


if __name__ == '__main__':
    main()

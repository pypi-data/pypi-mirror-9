#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
compute median of data
"""

# imports
import sys
from .filters import median
from .reduce import ReduceParser


__all__ = ['main']


def main(args=sys.argv[1:]):
    """CLI"""
    ReduceParser(median)(*args)


if __name__ == '__main__':
    main()



#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
personal experiments in plotting
"""

# imports
import argparse
import os
import subprocess
import sys

# module globals
__all__ = ['main', 'Parser']
here = os.path.dirname(os.path.realpath(__file__))
string = (str, unicode)

def ensure_dir(directory):
    """ensure a directory exists"""
    if os.path.exists(directory):
        assert os.path.isdir(directory)
        return directory
    os.makedirs(directory)
    return directory


class Parser(argparse.ArgumentParser):
    """CLI option parser"""
    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.options = None

    def parse_args(self, *args, **kw):
        options = argparse.ArgumentParser.parse_args(self, *args, **kw)
        self.validate(options)
        self.options = options
        return options

    def validate(self, options):
        """validate options"""

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = Parser()
    options = parser.parse_args(args)

if __name__ == '__main__':
    main()


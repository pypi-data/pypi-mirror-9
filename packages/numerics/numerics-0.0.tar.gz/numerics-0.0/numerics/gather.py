#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
gather files for processing
"""

import argparse
import os
import subprocess
import sys

__all__ = ['find', 'main']
string = (str, unicode)

def find(directories, filenames=None, exts=None):
    """gather files from directories"""


    retval = []
    if isinstance(directories, string):
        directories = [directories]

    directories = [os.path.abspath(d) for d in directories]

    for d in directories:

        if not os.path.exists(d):
            continue
        if not os.path.isdir(d):
            retval.append(d)
            continue

        for item in sorted(os.listdir(d)):
            path = os.path.join(d, item)

            if os.path.isdir(path):
                retval.extend(find(path, filenames=filenames, exts=exts))
            else:
                if filenames:
                    if item in filenames:
                        retval.append(path)
                elif exts:
                    for ext in exts:
                        if path.endswith(ext):
                            retval.append(path)
                            break
                else:
                    retval.append(path)

    return retval


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='+', help="paths")
    parser.add_argument('-e', '--ext', dest='exts',
                        nargs='+', help='extensions')
    options = parser.parse_args(args)

    # gather
    paths = find(options.path, exts=options.exts)

    # scatter
    print ('\n'.join(paths))

if __name__ == '__main__':
    main()

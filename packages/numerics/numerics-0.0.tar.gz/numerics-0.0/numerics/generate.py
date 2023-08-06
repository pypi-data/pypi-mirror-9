#!/usr/bin/env

"""
data generation

Should probably look at something like numpy for this
rather than rolling our own.  Bootstrapping...
"""

__all__ = ['frange']

def frange(xmin, xmax, n):
    """
    float range

    xmin -- left-hand range limiter
    xmax -- right-hand range limiter
    n -- number of slices (one less than number of points)
    """
    dx = (xmax - xmin)/float(n)
    retval = [xmin+dx*i for i in range(0,n)]
    retval.append(xmax)
    return retval

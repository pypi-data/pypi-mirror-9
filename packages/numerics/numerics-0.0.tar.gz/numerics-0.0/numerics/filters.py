"""
filter functions for stats
"""

__all__ = ['mean', 'array_mean', 'median']

def mean(data):
    return sum(data)/float(len(data))

def array_mean(data):
    if not data:
        return []
    lengths = [len(i) for i in data]
    if len(set(lengths)) != 1:
        raise AssertionError("Different lengths to array_mean: {}".format(' '.join(lengths)))
    return [mean(i) for i in zip(*data)]

def median(data):
    length = len(data)
    index = length/2
    if length % 2:
        return data[index]
    else:
        return 0.5*(data[index-1] + data[index])


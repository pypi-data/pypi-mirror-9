"""
csample: Sampling library for Python
"""
from __future__ import division
import argparse
import sys
import random
import itertools

import six
import xxhash
import spooky


__version__ = '0.4.0'
__all__ = [
    'sample_tuple', 'sample_line', 'reservoir',
    'main', 'parse_arguments',
    '__version__',
]


def main(args=None, sin=sys.stdin, sout=sys.stdout):
    a = parse_arguments(args)
    write = sout.write

    if a.method == 'hash':
        col = a.col
        sep = a.sep
        rate = a.rate
        funcname = a.hash
        seed = a.seed or 'DEFAULT_SEED'

        if col == -1:
            tuples = ((l,) for l in sin)
        else:
            tuples = ((l.split(sep)[col], l) for l in sin)

        for l in sample_tuple(tuples, rate, 0, funcname, seed):
            write(l[-1])
    elif a.method == 'reservoir':
        size = int(a.rate)
        seed = a.seed or None
        keep_order = a.order
        for l in reservoir(sin, size, seed, keep_order):
            write(l)


def parse_arguments(args):
    parser = argparse.ArgumentParser(description='Print sampled standard input')
    parser.add_argument(
        '-r', '--rate', type=float, required=True,
        help='sampling rate (in hash sampling mode) or reservior size (in reservior sampling mode)'
    )
    parser.add_argument(
        '-s', '--seed', type=str,
        help='seed for hash function (in hash sampling mode) or random seed (in reservior sampling mode)'
    )
    parser.add_argument('-c', '--col', type=int, default=-1, help='column index (starts from 0)')
    parser.add_argument('--method', type=str, default='hash', help='sampling method: hash (default) or reservoir')
    parser.add_argument('--hash', type=str, default='xxhash32', help='hash function: xxhash32 (default) or spooky32')
    parser.add_argument('--sep', type=str, default=',', help='column separator')
    parser.add_argument('--order', action='store_true', help='preserve input order')

    argdict = parser.parse_args(args)
    argdict.sep = six.u(argdict.sep)
    return argdict


def sample_tuple(s, rate, col, funcname='xxhash32', seed='DEFAULT_SEED'):
    """Sample tuples in given stream `s`.

    Performs hash-based sampling with given sampling `rate` by applying a hash
    function `funcname`. Sampling with the same `seed` always yields the same
    result.

    Following example shows how to sample approximately 50% of log data based
    on user ID column. Note that the returned value is a generator:

    >>> logs = (
    ...     # user id, event type, timestamp
    ...     ('alan', 'event a', 0),
    ...     ('alan', 'event b', 1),
    ...     ('brad', 'event a', 2),
    ...     ('cate', 'event a', 3),
    ...     ('cate', 'event a', 4),
    ...     ('brad', 'event b', 5),
    ...     ('brad', 'event c', 6),
    ...     ('daan', 'event a', 7),
    ...     ('daan', 'event b', 8),
    ... )
    >>> list(sample_tuple(logs, 0.5, 0))
    [('cate', 'event a', 3), ('cate', 'event a', 4), ('daan', 'event a', 7), ('daan', 'event b', 8)]

    :param s: stream of tuples
    :param rate: sampling rate from 0.0 to 1.0
    :param col: index of column to be hashed
    :param funcname: name of hash function: xxhash32 (default), spooky
    :param seed: seed for hash function
    :return: sampled stream of tuples
    """
    func = _hash_with_seed(funcname, seed)
    int_rate = int(rate * 0xFFFFFFFF)
    return (l for l in s if func(l[col]) < int_rate)


def sample_line(s, rate, funcname='xxhash32', seed='DEFAULT_SEED'):
    """Sample strings in given stream `s`.

    The function expects strings instead of tuples, except for that the
    function does the exactly same thing with `sample_tuple()`.

    :param s: stream of strings
    :param rate: sampling rate from 0.0 to 1.0
    :param funcname: name of hash function: xxhash32 (default), spooky
    :param seed: seed for hash function
    :return: sample stream of strings
    """
    tuples = ((l,) for l in s)
    return (
        l[-1] for l in sample_tuple(tuples, rate, 0, funcname, seed)
    )


def partition_tuple(s, ratios, col, funcname='xxhash32', seed='DEFAULT_SEED'):
    """Partition a stream of tuples into two or more streams based
    on hash value of specified column."""
    func = _hash_with_seed(funcname, seed)
    dart_ticks = [0] + [sum(ratios[:i+1]) * 0xFFFFFFFF for i in range(len(ratios))]
    dart_ticks[-1] = 0xFFFFFFFF

    tees = itertools.tee(s, len(ratios))
    ranges = [(dart_ticks[i], dart_ticks[i + 1]) for i in range(len(dart_ticks) - 1)]

    def _create_generator(stream, low, high):
        return (l for l in stream if low <= func(l[col]) < high)

    return [
        _create_generator(tee, low, high)
        for tee, (low, high) in zip(tees, ranges)
    ]


def partition_line(s, ratios, funcname='xxhash32', seed='DEFAULT_SEED'):
    """Partition a stream of lines into two or more streams based
    on hash value."""
    tuples = ((l,) for l in s)
    return (
        (l[-1] for l in stream)
        for stream in partition_tuple(tuples, ratios, 0, funcname, seed)
    )


def reservoir(s, size, seed=None, keep_order=False):
    """Perform reservoir sampling.

    >>> logs = (
    ...     'alan',
    ...     'brad',
    ...     'cate',
    ...     'daan',
    ... )
    >>> samples = reservoir(logs, 2)
    >>> len(samples), len(set(samples))
    (2, 2)
    >>> set(samples).issubset(set(logs))
    True

    :param s: stream of anything
    :param size: sample size
    :param seed: optional seed (any hashable object)
    :param keep_order: force elements in sample to respect input order
    :return: sampled list
    """
    if seed is not None:
        random.seed(seed)

    buckets = []
    s = iter(s)

    # 1. Initial phase to fill reservoir
    k = 0
    for i in range(size):
        buckets.append((k, next(s)))
        k += 1

    # 2. Probabilistic update
    for l in s:
        position = random.randint(0, k)
        if position < size:
            buckets[position] = (k, l)
        k += 1

    if keep_order:
        buckets = sorted(buckets, key=lambda x: x[0])

    return [e[1] for e in buckets]


def _hash_with_seed(funcname, seed):
    seed = xxhash.xxh32(seed).intdigest()

    xxh32 = xxhash.xxh32
    spooky32 = spooky.hash32

    if funcname == 'xxhash32':
        return lambda x: xxh32(x, seed=seed).intdigest()
    elif funcname == 'spooky32':
        return lambda x: spooky32(x, seed=seed)
    else:
        raise ValueError('Unknown function name: %s' % funcname)


class HashSampler(object):
    """Class-based interface for hash sampling.

    >>> sampler = HashSampler()
    >>> rate = 0.5
    >>> sampler.should_sample('alan', rate)
    False
    >>> sampler.should_sample('brad', rate)
    False
    >>> sampler.should_sample('cate', rate)
    True
    >>> sampler.should_sample('daan', rate)
    True
    """
    def __init__(self, funcname='xxhash32', seed='DEFAULT_SEED'):
        """
        Create an instance of HashSample

        :param funcname: name of hash function: xxhash32 (default), spooky
        :param seed: seed for hash function
        """
        self._func = _hash_with_seed(funcname, seed)

    def should_sample(self, data, rate):
        """
        Checks whether or not to sample data

        :param data: any str to be hashed
        :param rate: sampling rate from 0.0 to 1.0
        """
        int_rate = int(rate * 0xFFFFFFFF)
        return self._func(data) < int_rate


if __name__ == '__main__':
    main()

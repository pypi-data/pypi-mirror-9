csample: Sampling library for Python
====================================

|travismaster| |coverage|

.. |travismaster| image:: https://travis-ci.org/box-and-whisker/csample.svg
   :target: http://travis-ci.org/box-and-whisker/csample

.. |coverage| image:: https://img.shields.io/coveralls/box-and-whisker/csample.svg
   :target: https://coveralls.io/r/box-and-whisker/csample?branch=master

``csample`` provides pseudo-random sampling methods applicable when the size
of population is unknown:

*   Use hash-based sampling to fix sampling rate
*   Use reservoir sampling to fix sample size

Hash-based sampling
===================

Hash-based sampling is a filtering method that tries to approximate random
sampling by using a hash function as a selection criterion.

Following list describes some features of the method:

*   Since there are no randomness involved at all, the same data set with the
    same sampling rate (and also with the same salt value) always yields
    exactly the same result.
*   The size of population doesn't need to be specified beforehand. It means
    that the sampling process can be applied to data stream with unknown size
    such as system logs.

Here are some real and hypothetical applications:

*   `[RFC5475] Sampling and Filtering Techniques for IP Packet Selection <https://tools.ietf.org/html/rfc5475>`_
    is a well-known application.
*   Online streaming algorithm to select 10% of users for A/B testing.
    "Consistent" nature of the algorithm guarantees that any user ID selected
    once will always be selected again. There's no need to maintain a list of
    selected user IDs.

``csample`` provides two sampling functions for a convenience.

``sample_line()`` accepts iterable type containing strs::

    data = [
        'alan',
        'brad',
        'cate',
        'david',
    ]
    samples = csample.sample_line(data, 0.5)

``sample_tuple()`` expects tuples instead of strs as a content of
iterable. The third argument 0 indicates a column index::

    data = [
        ('alan', 10, 5),
        ('brad', 53, 7),
        ('cate', 12, 6),
        ('david', 26, 5),
    ]
    samples = csample.sample_tuple(data, 0.5, 0)

In both cases, the function returns immediately with sampled iterable.


Reservoir sampling
==================

Reservoir sampling is a family of randomized algorithms for randomly choosing
a sample of k items from a list S containing n items, where n is either a very
large or unknown number.

You can specify random seed to perform reproducible sampling.

For more information, read `Wikipedia <http://en.wikipedia.org/wiki/Reservoir_sampling>`_

``csample`` provides single function for reservoir sampling::

    data = [
        'alan',
        'brad',
        'cate',
        'david',
    ]
    samples = csample.reservoir(data, 2)

Resulting ``samples`` contains two elements randomly choosen from given ``data``.

Note that the function doesn't return a generator but list, and also won't
finish until it consume the entire input stream.

Also note that, by default, reservoir sampling doesn't preserve order of original
list which means that following assertion holds in general::

   population = [0, 1, 2, 3, 4, 5]
   samples = csample.reservoir(population, 3)
   assert sorted(samples) != samples

To maintain original order, provide ``keep_order=True`` parameter::

   population = [0, 1, 2, 3, 4, 5]
   samples = csample.reservoir(population, 3, keep_order=True)
   assert sorted(samples) == samples


API documentation
=================

Read the `full API documentation. <https://csample.readthedocs.org/en/latest/>`_


Command-line interface
======================

``csample`` also provides command-line interface.

Following command prints 50% sample from 100 integers::

    > seq 100 | csample -r 0.5

To see more options use ``--help`` command-line argument::

    > csample --help


Hash functions
==============

In order to obtain fairly random/unbiased sample, it is critical to use suitable
hash function.

There could be many criteria such as `avalanche effect <http://en.wikipedia.org/wiki/Avalanche_effect>`_.
For those who are interested, see link below:

*   `Empirical Evaluation of Hash Functions for Multipoint Measurements <http://www.sigcomm.org/sites/default/files/ccr/papers/2008/July/1384609-1384614.pdf>`_

Hash-based sampling implemented in ``csample`` currently supports `xxhash`_
and `spooky`_.

.. _xxhash: https://code.google.com/p/xxhash/
.. _spooky: http://burtleburtle.net/bob/hash/spooky.html


Installation
============

Installing csample is easy::

    pip install csample

or download the source and run::

    python setup.py install

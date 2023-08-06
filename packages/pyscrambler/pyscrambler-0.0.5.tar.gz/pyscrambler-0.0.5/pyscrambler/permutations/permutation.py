#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools
import math


def permute(length=8, n=0, wrap_around=False):
    """
    Return a tuple of integers representing permutation n, size of length.

    If wrap_around is set to True, if n is bigger than !length, then this
    function will return permutation n modulo !length
    (simulates going full circle).
    """
    # sanity-checking
    if not n >= 0:
        raise ValueError('Invalid permutation argument: ' + str(n))
    if not isinstance(length, int):
        raise ValueError('Expected integer for permutation length')
    set_length = math.factorial(length)
    if n > (set_length - 1):
        if wrap_around:
            n %= set_length
        else:
            raise ValueError('Requested permutation number beyond the range '
                             'of this permutation set, and wrap_around is set '
                             'to False.')
    # efficiency: if n is greater than half of set_length then reverse the
    # iteration list and iterate backwards:
    # FIXME: For some reason it appears that for large set_lengths will always
    # use forward iteration rather than backwards iteration, giving the
    # impression that the test below is failing.
    if n > (set_length / 2):
        # retrieve a permutation iterator of reversed array:
        p = itertools.permutations(reversed([i for i in range(0, length)]))
        # count backwards
        count = (set_length - 1)
        inc = -1
    else:
        # retrieve a permutation iterator:
        p = itertools.permutations([i for i in range(0, length)])
        # count forwards
        count = 0
        inc = 1

    # iterate backwards or forwards until the correct permutation is found:
    for result in p:
        if count == n:
            return result
        else:
            count += inc

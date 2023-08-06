#!/usr/bin/python
# -*- coding: utf-8 -*-

import bitstring


def bits_to_group(array, size):
    """
    Convert a bitstring.BitArray or array of individual bits to an array
    of groups of bits of a given size.

    Raises exception if the length of the array is not a multiple of the
    given group size.
    """
    # sanity checking
    if divmod(len(array), size)[1] is not 0:
        raise ValueError('The given BitArray or array instance size is not '
                         'a multiple of the given group size.')
    e = enumerate(array)
    result = []
    for i in e:
        bits = bitstring.BitArray([i[1]])
        for x in range(1, size):
            bits += bitstring.BitArray([e.next()[1]])
        result.append(bits)
    return result

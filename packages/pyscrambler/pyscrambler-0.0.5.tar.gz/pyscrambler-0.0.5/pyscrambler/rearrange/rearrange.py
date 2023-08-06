#!/usr/bin/python
# -*- coding: utf-8 -*-


def re_arrange(data_array, order_array):
    """
    Re-arrange the items in data_array to be
    in the order specified by order_array.
    """
    # sanity checking
    if not hasattr(data_array, '__iter__'):
        raise TypeError('Non-iterable type passed as data_array argument.')
    if not hasattr(order_array, '__iter__'):
        raise TypeError('Non-iterable type passed as order_array argument.')
    if len(order_array) is not len(data_array):
        raise ValueError('data_array and order_array length do not match.')
    length = len(data_array)
    new_array = [None] * length
    for norm, index in enumerate(order_array):
        new_array[norm] = data_array[index]
    return new_array


def reverse_order(order_array):
    """
    Returns the effective 'inverse' of the given order array, that is by
    returning the order array that would be needed to re-arrange back to the
    correct order.
    """
    # sanity checking
    if not hasattr(order_array, '__iter__'):
        raise TypeError('Non-iterable type passed as order_array argument.')
    length = len(order_array)
    new_array = [None] * length
    for index, replace in enumerate(order_array):
        new_array[replace] = index
    return new_array

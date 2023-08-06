# -*- coding: utf-8 -*-
"""
wrapper for core low-level methods.
"""

from shifty import RIGHT, LEFT, WRAP, SHIFT
from shifty import DEFAULT_VALUE
from shifty.action import action_
from shifty.action import set_items as set_items_
from shifty.action import clear_items as clear_items_
from shifty.action import get as get_
from shifty.action import iget as iget_


def wrap(iterable, count, in_place=True, direction=RIGHT):
    """
    Wrap the sliceable iterable 'iterable', 'count' places to the 'direction'.
    The wrap is modulo the length of the array.
    :param iterable: The iterable to wrap
    :param count: The number of places to wrap
    :param in_place: True: Perform the operation in-place, (False-default).
    :return: The shifted iterable.
    """
    return action_(WRAP, iterable, count, in_place, direction)


def shift(iterable, count, in_place=True, direction=RIGHT,
          default_value=DEFAULT_VALUE):
    """
    Shift the sliceable iterable 'iterable', 'count' places to the 'direction'.
    :param iterable: The iterable to shift
    :param count: The number of places to shift
    :param in_place: True: Perform the operation in-place, (False-default).
    :param default_value: The default value to use.
    :return: The shifted iterable.
    """
    return action_(SHIFT, iterable, count, in_place, direction,
                   default_value=default_value)


def wrap_right(iterable, count, in_place=True):
    """
    Convenience wrapper for method: 'wrap(right)'.
    Wrap the sliceable iterable 'iterable', 'count' places to the right.
    The wrap is modulo the length of the array.
    :param iterable: The iterable to wrap
    :param count: The number of places to wrap
    :param in_place: True: Perform the operation in-place, (False-default).
    :return: The wrapped iterable.

    eg:
    >>> a = [1, 2, 3, 4]
    >>> b = wrap_right(a, 3, in_place=False)
    >>> b
    [2, 3, 4, 1]
    >>> assert a is not b

    >>> b = wrap_right(a, 2, in_place=True)
    >>> assert a is b

    >>> b = wrap_right(a, 5, in_place=False)
    >>> b
    [2, 3, 4, 1]
    """
    return wrap(iterable, count, in_place=in_place, direction=RIGHT)


def wrap_left(iterable, count, in_place=True):
    """
    Convenience wrapper for method: 'wrap(left)'.
    Wrap the sliceable iterable 'iterable' 'count' places to the left.
    The wrap is modulo the length of the array.
    :param iterable: The iterable to wrap
    :param count: The number of places to wrap
    :param in_place: True: Perform the operation in-place, (False-default).
    :return: The wrapped iterable.

    eg:
    >>> a = [1, 2, 3, 4]
    >>> b = wrap_left(a, 3, in_place=False)
    >>> b
    [4, 1, 2, 3]
    >>> assert a is not b

    >>> b = wrap_left(a, 2, in_place=True)
    >>> assert a is b

    >>> b = wrap_left(a, 5, in_place=False)
    >>> b
    [4, 1, 2, 3]
    """
    return wrap(iterable, count, in_place=in_place, direction=LEFT)


def shift_right(iterable, count, in_place=True, default_value=DEFAULT_VALUE):
    """
    Convenience wrapper for method: 'shift(right)'.
    Shift the sliceable iterable 'iterable' 'count' places to the right.
    The shift is modulo the length of the array.
    :param iterable: The iterable to shift
    :param count: The number of places to shift
    :param in_place: True: Perform the operation in-place, (False-default).
    :param default_value: The default value to use.
    :return: The shifted iterable.

    eg:
    >>> a = [1, 2, 3, 4]
    >>> b = shift_right(a, 3, in_place=False)
    >>> b
    [None, None, None, 1]
    >>> assert a is not b

    >>> b = shift_right(a, 2, in_place=True)
    >>> assert a is b
    >>> b
    [None, None, 1, 2]

    >>> b = shift_right(a, 5, in_place=False)
    >>> b
    [None, None, None, None]
    """
    return shift(iterable, count, in_place=in_place, direction=RIGHT,
                 default_value=default_value)


def shift_left(iterable, count, in_place=True, default_value=DEFAULT_VALUE):
    """
    Convenience wrapper for method: 'shift(left)'.
    Shift the sliceable iterable 'iterable' 'count' places to the left.
    The shift is modulo the length of the array.
    :param iterable: The iterable to shift
    :param count: The number of places to shift
    :param in_place: True: Perform the operation in-place, (False-default).
    :param default_value: The default value to use.
    :return: The shifted iterable.

    eg:
    >>> a = [1, 2, 3, 4]
    >>> b = shift_left(a, 3, in_place=False)
    >>> b
    [4, None, None, None]
    >>> assert a is not b

    >>> b = shift_left(a, 2, in_place=True)
    >>> b
    [3, 4, None, None]
    >>> assert a is b

    >>> b = shift_left(a, 5, in_place=False)
    >>> b
    [None, None, None, None]
    """
    return shift(iterable, count, in_place=in_place, direction=LEFT,
                 default_value=default_value)

# Aliases:
wl = wrap_left
wr = wrap_right
sl = shift_left
sr = shift_right


def set_items(iterable, items, indexes, in_place=False, **kwargs):
    return set_items_(iterable, items, indexes, in_place=in_place,
                      **kwargs)


def clear_items(iterable, indexes, in_place=False, **kwargs):
    return clear_items_(iterable, indexes, in_place=in_place, **kwargs)


def xset_items(iterable, items, indexes, in_place=False, **kwargs):
    return set_items_(iterable, items, indexes, invert=True, in_place=in_place,
                      **kwargs)


def xclear_items(iterable, indexes, in_place=False, **kwargs):
    return clear_items_(iterable, indexes, invert=True, in_place=in_place,
                        **kwargs)


def get(iterable, indexes, **kwargs):
    return get_(iterable, indexes, invert=False, **kwargs)


def iget(iterable, indexes, **kwargs):
    return iget_(iterable, indexes, invert=False, **kwargs)


def xget(iterable, indexes, **kwargs):
    return get_(iterable, indexes, invert=True, **kwargs)


def ixget(iterable, indexes, **kwargs):
    return iget_(iterable, indexes, invert=True, **kwargs)


if __name__ == '__main__':  # pragma no cover
    pass

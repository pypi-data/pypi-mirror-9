# -*- coding: utf-8 -*-
"""
Various utilities.
"""

from shifty import WRAP, SHIFT
from shifty.interfaces import base_api


def determine_count(action, count, a):
    # Fix and determine count:
    count = abs(count)
    if action == WRAP:
        # Only makes sense for wrapping, not shifting.
        count %= len(a)
    elif action == SHIFT:
        # No point shifting more than we need to:
        l = len(a)
        count = count if count < l else l
    return count


def get_class(a):
    if isinstance(a, base_api):
        return a.__class__
    elif isinstance(a, list):
        return list
    raise ValueError('unable to get class: %s' % a)


def clear_instance(a, clear=None):
    """
    clear the class in-place.
    """
    if isinstance(a, base_api):
        if clear is not None:
            a.clear()
            if isinstance(clear, list):
                a.extend(clear)
        return a
    elif isinstance(a, list):
        del a[:]
        if clear is not None:
            if isinstance(clear, list):
                a.extend(clear)
        return a
    raise ValueError('unable to clear class: %s' % a)


def new_class(a, clear=None):
    """
    Create a new instance of the given class.
    :param a: The item in question.
    :param clear: True - clear out the contents of cls, False - otherwise.
    :return: An instance of the new class.
    """
    cls = get_class(a)
    result = cls(a)
    result = clear_instance(result, clear=clear)
    return result


def forever(value):
    while True:
        yield value


def item_to_iterable(item):
    if isinstance(item, tuple):
        return list(item)
    elif isinstance(item, int):
        return [item]
    else:
        return item if isinstance(item, list) else [item]


def xiter(iter_indexes, start=0, end=None):
    """
    Create an iterator that yields indexes from iterable not contained in
    iter_indexes.

    :type iter_indexes: iterator, the indexes (ALWAYS SORTED).
    :type start: int, the primary index to start at.
    :return: An iterator performing the requested action.
    """
    if not isinstance(start, int):
        raise TypeError('start must be an integer but got: %s' % type(start))
    if start < 0:
        raise ValueError(
            'start must be greater or equal to zero, got: %s' % start)

    def inversion_iterator():
        index = start
        for i in iter_indexes:
            while index < i:
                yield index
                index += 1
            if index == i:
                index += 1
        while index <= end if end else True:
            yield index
            index += 1

    return inversion_iterator()


if __name__ == '__main__':  # pragma no cover
    pass

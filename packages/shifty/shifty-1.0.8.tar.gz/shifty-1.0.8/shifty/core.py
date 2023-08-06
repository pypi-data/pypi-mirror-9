# -*- coding: utf-8 -*-
"""
Core low-level self-contained methods.
"""

from itertools import repeat
from six import advance_iterator
from six.moves import range
from shifty import LEFT, RIGHT, WRAP, SHIFT


def _wrap_left(a, count, in_place, *args):
    if in_place:
        for _ in range(count):
            a.append(a.pop(0))
        return a
    else:
        return a[count:] + a[:count]


def _wrap_right(a, count, in_place, *args):
    if in_place:
        for _ in range(count):
            a.insert(0, a.pop(-1))
        return a
    else:
        return a[-count:] + a[:-count]


def _wrap(direction, a, count, in_place, *args):
    if direction == LEFT:
        return _wrap_left(a, count, in_place)
    elif direction == RIGHT:
        return _wrap_right(a, count, in_place)


def _shift_left(a, count, in_place, default_value):
    if in_place:
        for _ in range(count):
            a.pop(0)
            a.append(default_value)
        return a
    else:
        return a[count:] + _empty_list(count, default_value)


def _shift_right(a, count, in_place, default_value):
    if in_place:
        for _ in range(count):
            a.pop(-1)
            a.insert(0, default_value)
        return a
    else:
        return _empty_list(count, default_value) + a[:len(a) - count]


def _shift(direction, a, count, in_place, default_value):
    if direction == LEFT:
        return _shift_left(a, count, in_place, default_value)
    elif direction == RIGHT:
        return _shift_right(a, count, in_place, default_value)


def _determine_count(action, count, a):
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


def _empty_list(count, default_value):
    return list(repeat(default_value, count))


def _set_item(a, index, value):
    a[index] = value


def _get_item(a, index, **kwargs):
    try:
        return a[index]
    except IndexError:
        if 'default_value' in kwargs:
            return kwargs['default_value']
        raise


def _set_items(iterable, indexes, items):
    while True:
        try:
            index = advance_iterator(indexes)
        except StopIteration:
            break

        try:
            value = advance_iterator(items)
        except StopIteration:
            break

        _set_item(iterable, index, value)
    return iterable


def _get_items(iterable, indexes, default_item):
    return list(_iget_items(iterable, indexes, default_item))


def _iget_items(iterable, indexes, default_item):
    while True:
        try:
            index = advance_iterator(indexes)
        except StopIteration:
            break

        try:
            default_item_ = advance_iterator(default_item)
        except Exception:
            yield _get_item(iterable, index)
        else:
            yield _get_item(iterable, index, default_value=default_item_)


if __name__ == '__main__':  # pragma: no cover
    pass

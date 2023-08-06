# -*- coding: utf-8 -*-
"""
Low-level actions.
"""

from shifty import WRAP, SHIFT, LEFT, RIGHT, SET, CLEAR
from shifty.caller import CallerData
from shifty.errors import CriticalError
from shifty.core import _wrap, _shift, _set_items, _get_items, _iget_items
from shifty.utils import new_class, forever, item_to_iterable, xiter, \
    determine_count

DIRECTIONS = [LEFT, RIGHT]
ACTIONS = [WRAP, SHIFT]
SETTERS = [SET, CLEAR]
MAX_ERROR_COUNT = 2
_DEFAULT_SETTER_VALUE = None
_DEFAULT_GETTER_VALUE = None


def get(iterable, indexes, invert=False, **kwargs):
    """
    get items at given indexes

    :type iterable: list, the input list to modify.
    :type indexes: int/list(int), The indexes to set.
    :type invert: bool, Invert the indexes (clear non-indexed items).
    :type kwargs['default_value']: The default value to use, defaults to None.
    :return: The modified iterable.
    """
    return _do_get(iterable, indexes, invert=invert, iterator=False, **kwargs)


def iget(iterable, indexes, invert=False, **kwargs):
    """
    get items at given indexes

    :type iterable: list, the input list to modify.
    :type indexes: int/list(int), The indexes to set.
    :type invert: bool, Invert the indexes (clear non-indexed items).
    :type kwargs['default_value']: The default value to use, defaults to None.
    :type kwargs['end']: Stop getting the iterable when the index reaches this
        value.
    :return: The modified iterable.
    """
    return _do_get(iterable, indexes, invert=invert, iterator=True, **kwargs)


def _do_get(iterable, indexes, invert=False, iterator=False, **kwargs):
    def get_return_value(i, clear=None):
        return new_class(i, clear=clear)

    # error-check:
    if iterable is None:
        raise ValueError('iterable must be provided')

    if not indexes:
        return get_return_value(iterable, clear=True)
    if not isinstance(indexes, (list, tuple, int)):
        raise ValueError('indexes not specified correctly: %s' % indexes)
    indexes = item_to_iterable(indexes)

    items = forever(kwargs.get('default_value', _DEFAULT_GETTER_VALUE))
    end = kwargs.get('end', None)
    indexes = iter(indexes)
    indexes = xiter(indexes, end=end) if invert else indexes

    if iterator:
        return _iget_items(get_return_value(iterable), indexes, items)
    return get_return_value(iterable,
                            clear=_get_items(iterable, indexes, items))


def set_items(iterable, items, indexes, in_place, invert=False, **kwargs):
    """
    set items at given indexes

    :type iterable: list, the input list to modify.
    :type items: object/list(object), The items to set at the given indixes.
    :type indexes: int/list(int), The indexes to set.
    :type in_place: bool, True - modify in-place, False - otherwise.
    :type invert: bool, Invert the indexes (clear non-indexed items).
    :type kwargs['default_value']: The default value to use, defaults to None.
    :return: The modified iterable.
    """
    # Determine params:
    in_place = CallerData.get_value(in_place)

    def get_return_value():
        return iterable if in_place else new_class(iterable)

    # error-check:
    if iterable is None:
        raise ValueError('iterable must be provided')

    if indexes is None:
        return get_return_value()
    if not isinstance(indexes, (list, tuple, int)):
        raise ValueError('indexes not specified correctly: %s' % indexes)
    indexes = item_to_iterable(indexes)

    using_default = False
    if items is None or (isinstance(items, (list, tuple)) and len(items) == 0):
        if 'default_value' not in kwargs:
            return get_return_value()
        items = forever(kwargs['default_value'])
        using_default = True

    if not isinstance(items, (list, tuple)) and not using_default:
        items = item_to_iterable(items)
    if not items:  # pragma no cover (just in case)
        return get_return_value()

    items = iter(items)
    indexes = iter(indexes)
    indexes = xiter(indexes) if invert else indexes

    return _set_items(get_return_value(), indexes, items)


def clear_items(iterable, indexes, in_place, invert=False, **kwargs):
    """
    clear items at given indexes

    :type iterable: list, the input list to modify.
    :type indexes: int/list(int), The indexes to set.
    :type in_place: bool, True - modify in-place, False - otherwise.
    :type invert: bool, Invert the indexes (clear non-indexed items).
    :type kwargs['default_value']: The default value to use, defaults to None.
    :return: The modified iterable.
    """
    # Determine params:
    in_place = CallerData.get_value(in_place)

    def get_return_value():
        return iterable if in_place else new_class(iterable)

    # error-check:
    if iterable is None:
        raise ValueError('iterable must be provided')

    if indexes is None:
        return get_return_value()
    if not isinstance(indexes, (list, tuple, int)):
        raise ValueError('indexes not specified correctly: %s' % indexes)
    indexes = item_to_iterable(indexes)

    items = forever(kwargs.get('default_value', _DEFAULT_SETTER_VALUE))
    indexes = iter(indexes)
    indexes = xiter(indexes) if invert else indexes

    return _set_items(get_return_value(), indexes, items)


def action_(action, iterable, count, in_place, direction, default_value=None):
    """
    Shift a sliceable iterable 'iterable', abs('count') places to the right.
    If the shift is greater than the length of the array,then the shift is the
    modulo of the shift wrt the length of the iterable.
    :type iterable: list, the input list to shift.
    :type count: int, The number of places to shift (abs value used).
    :type in_place: bool, True - modify in-place, False - otherwise.
    :type direction: one of [LEFT, RIGHT].
    :type wrap: bool, True - wrap values in list, False - otherwise.
    :type default_value: The default value to use, defaults to None.
    :return: The modified iterable.
    """
    # Determine params:
    count = CallerData.get_value(count)
    in_place = CallerData.get_value(in_place)
    direction = CallerData.get_value(direction)
    action = CallerData.get_value(action)

    # error-check:
    if not isinstance(count, int):
        raise ValueError('count must be an integer but got: %s: %s' % (type(
            count), count))
    if direction not in DIRECTIONS:
        raise ValueError('Unknown direction: %s' % direction)
    if action not in ACTIONS:
        raise ValueError('Unknown action: %s' % action)

    count = determine_count(action, count, iterable)

    if count:
        try:
            func = {WRAP: _wrap, SHIFT: _shift}[action]
        except KeyError:  # pragma no cover
            # This means our error-checking (above) didn't cover all cases.
            raise CriticalError(
                'Unable to determine operation on action: %s, %s' % action)
        return func(direction, iterable, count, in_place, default_value)
    return iterable


if __name__ == '__main__':  # pragma: no cover
    pass

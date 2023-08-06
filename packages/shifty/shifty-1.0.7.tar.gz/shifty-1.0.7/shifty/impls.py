# -*- coding: utf-8 -*-

"""
The shifty iterators.
"""

from six import wraps

from shifty import DEFAULT_VALUE, WRAP, SHIFT, LEFT, RIGHT
from shifty.action import action_, set_items, clear_items, get, iget
from shifty.interfaces import shift_api, wrap_api, helpers_api
from shifty.iterators import ShiftyWatcher, ShiftyIndexWatcher


def _shifter(func):
    """
    Decorator.
    Always return an instance of shifty if the input was also an instance of
    shifty.
    The resultant shifty instance has the same default_value as the original
    list if the original list is an instance of shifty,=.

    :param func: The function to wrap.
    :return: The decorated method.
    """

    @wraps(func)
    def _inner(*args, **kwargs):
        is_shifty = (args[0].__class__ == shifty)
        if is_shifty:
            default_value = args[0].default_value
        result = func(*args, **kwargs)
        if is_shifty and not isinstance(result, shifty):
            result = shifty(result)
            # Now copy the default_value:
            result.default_value = default_value
        return result

    return _inner


class shifty(list, shift_api, wrap_api, helpers_api):
    """
    Convenience class for shifty operations.
    """

    def clear(self):
        del self[:]
        return self

    def reset(self):
        self.default_value = DEFAULT_VALUE

    @property
    def default_value(self):
        if not hasattr(self, '_default_value'):
            self.default_value = DEFAULT_VALUE
        return getattr(self, '_default_value')

    @default_value.setter
    def default_value(self, default_value):
        setattr(self, '_default_value', default_value)

    @_shifter
    def action(self, action, count, in_place, direction, **kwargs):
        return action_(action, self, count, in_place, direction,
                       default_value=kwargs.get('default_value',
                                                self.default_value))

    def shift(self, count, in_place=True, direction=None, **kwargs):
        return self.action(SHIFT, count, in_place, direction, **kwargs)

    def shift_left(self, count, in_place=True, **kwargs):
        return self.action(SHIFT, count, in_place, LEFT, **kwargs)

    def shift_right(self, count, in_place=True, **kwargs):
        return self.action(SHIFT, count, in_place, RIGHT, **kwargs)

    def sl(self, count, in_place=True, **kwargs):
        return self.shift_left(count, in_place=True, **kwargs)

    def sr(self, count, in_place=True, **kwargs):
        return self.shift_right(count, in_place=True, **kwargs)

    def wrap(self, count, in_place=True, direction=None):
        return self.action(WRAP, count, in_place, direction)

    def wrap_left(self, count, in_place=True):
        return self.action(WRAP, count, in_place, LEFT)

    def wrap_right(self, count, in_place=True):
        return self.action(WRAP, count, in_place, RIGHT)

    def wl(self, count, in_place=True):
        return self.wrap_left(count, in_place=True)

    def wr(self, count, in_place=True):
        return self.wrap_right(count, in_place=True)

    def iter(self, count, direction, in_place=True, action=WRAP, **kwargs):
        """
        Return an iterable over the list as a whole

        :return: type(Iterable).

        eg:DEFAULT_VALUE
        >>> from shifty import LEFT
        >>> a = shifty([1, 2, 3, 4])
        >>> b = a.iter(3, LEFT, in_place=True, action=WRAP)
        >>> v = b.next()
        >>> assert a is v
        >>> assert v == [4, 1, 2, 3]

        >>> v = b.next()
        >>> assert a is v
        >>> assert v == [3, 4, 1, 2]
        """
        return ShiftyWatcher(self, count, direction, in_place=in_place,
                             action=action,
                             default_value=kwargs.get('default_value',
                                                      self.default_value))

    def iterindex(self, index, count, direction, in_place=True, action=WRAP,
                  **kwargs):
        """
        Return an iterable over the value of an element at a fixed index in
        the list.

        :return: type(Iterable).

        eg:
        >>> from shifty import LEFT
        >>> a = shifty([1, 2, 3, 4])
        >>> b = a.iterindex(1, 3, LEFT, in_place=False, action=WRAP)
        >>> v = b.next()
        >>> assert v == 1


        >>> v = b.next()
        >>> assert v == 4
        """
        return ShiftyIndexWatcher(self, index, count, direction,
                                  in_place=in_place, action=action,
                                  default_value=kwargs.get('default_value',
                                                           self.default_value))

    def set_items(self, items, indexes=None, in_place=False, **kwargs):
        return set_items(self, items, indexes, in_place,
                         default_value=kwargs.get('default_value',
                                                  self.default_value))

    def clear_items(self, indexes=None, in_place=False, **kwargs):
        return clear_items(self, indexes, in_place,
                           default_value=kwargs.get('default_value',
                                                    self.default_value))

    def xset_items(self, items, indexes=None, in_place=False, **kwargs):
        return set_items(self, items, indexes, in_place, invert=True,
                         default_value=kwargs.get('default_value',
                                                  self.default_value))

    def xclear_items(self, indexes=None, in_place=False, **kwargs):
        return clear_items(self, indexes, in_place, invert=True,
                           default_value=kwargs.get('default_value',
                                                    self.default_value))

    def get(self, indexes=None, **kwargs):
        return get(self, indexes, invert=False,
                   default_value=kwargs.get('default_value',
                                            self.default_value))

    def iget(self, indexes=None, **kwargs):
        return iget(self, indexes, invert=False,
                    default_value=kwargs.get('default_value',
                                             self.default_value))

    def xget(self, indexes=None, **kwargs):
        return get(self, indexes, invert=True,
                   default_value=kwargs.get('default_value',
                                            self.default_value),
                   end=kwargs.get('end', None))

    def ixget(self, indexes=None, **kwargs):
        return iget(self, indexes, invert=True,
                    default_value=kwargs.get('default_value',
                                             self.default_value),
                    end=kwargs.get('end', None))


if __name__ == '__main__':  # pragma no cover
    pass

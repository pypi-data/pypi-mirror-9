# -*- coding: utf-8 -*-

"""
The shifty iterators.
"""

from abc import ABCMeta
from collections import Iterable
from six import add_metaclass

from shifty import WRAP, DEFAULT_VALUE
from shifty.action import action_


@add_metaclass(ABCMeta)
class ShiftyIterable(Iterable):
    def __iter__(self):  # pragma no cover
        return self


class ShiftyWatcher(ShiftyIterable):
    """
    Shifty iterable over the entire list at once.
    """

    def __init__(self, s, count, direction, in_place=True, action=WRAP,
                 default_value=DEFAULT_VALUE):
        """
        :type s: Iterable, The iterable.
        :type count: int, The number of places to wrap.
        :type direction: str, one of [LEFT, RIGHT].
        :type in_place: bool, True - modify in-place, False - otherwise.
        :type action: str, one of [SHIFT, WRAP].
        :param default_value: The default value to use.
        """
        self._s = s
        self._count = count
        self._direction = direction
        self._in_place = in_place
        self.action_ = action
        self._default_value = default_value

    def next(self):
        self._s = action_(self.action_, self._s, self._count,
                          in_place=self._in_place,
                          direction=self._direction,
                          default_value=self._default_value)
        return self._s


class ShiftyIndexWatcher(ShiftyIterable):
    """
    Shifty iterable over an individual item in the list.
    """

    def __init__(self, s, index, count, direction, in_place=True,
                 action=WRAP, default_value=DEFAULT_VALUE):
        """
        :type s: Iterable, The iterable.
        :type index: int, The index to watch.
        :type count: int, The number of places to wrap.
        :type direction: one of [LEFT, RIGHT].
        :type in_place: bool, True - modify in-place, False - otherwise.
        :type action: str, one of [SHIFT, WRAP].
        :param default_value: The default value to use.
        """
        self._s = s
        self._index = index
        self._count = count
        self._direction = direction
        self._in_place = in_place
        self.action_ = action
        self._default_value = default_value

    def next(self):
        self._s = action_(self.action_, self._s, self._count,
                          in_place=self._in_place,
                          direction=self._direction,
                          default_value=self._default_value)
        return self._s[self._index]


if __name__ == '__main__':  # pragma no cover
    pass

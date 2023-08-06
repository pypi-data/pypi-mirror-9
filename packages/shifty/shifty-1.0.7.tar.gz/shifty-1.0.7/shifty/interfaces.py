# -*- coding: utf-8 -*-
"""
The shifty class api.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from six import add_metaclass


@add_metaclass(ABCMeta)
class base_api(object):  # pragma no cover
    @abstractmethod
    def clear(self):
        """
        Clear the shifty items.
        :return: self
        """
        raise NotImplementedError()

    @abstractmethod
    def reset(self):
        """
        Reset the shifty variable instance attributes.
        :return:
        """
        raise NotImplementedError()

    @abstractproperty
    def default_value(self):
        """
        Retrieve the default_value for all empty list items that need creation.

        :return: The default item, defaults to 'DEFAULT_VALUE'.
        """
        raise NotImplementedError()

    @abstractproperty
    @default_value.setter
    def default_value(self, default_value):
        """
        Set the default_value for all empty list items from shift
        operations.
        :param default_value: The default value to use in the absence of an
        override in a shifty method.
        """
        raise NotImplementedError()

    @abstractmethod
    def action(self, action, count, in_place, direction, **kwargs):
        """
        All actions available from here.

        :type action: one of [SHIFT, WRAP].
        :type count: int, The number of places to shift.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :type direction: one of [LEFT, RIGHT].
        :param kwargs['default_value']: The default value to use.
        :return: The modified iterable.
        """
        raise NotImplementedError()


@add_metaclass(ABCMeta)
class shift_api(base_api):  # pragma no cover
    @abstractmethod
    def shift(self, count, in_place=True, direction=None, **kwargs):
        """
        shift

        :type count: int, The number of places to shift.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :type direction: one of [LEFT, RIGHT].
        :param kwargs['default_value']: The default value to use.
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def shift_left(self, count, in_place=True, **kwargs):
        """
        Convenience method for: shift-left

        :type count: int, The number of places to shift.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :param kwargs['default_value']: The default value to use.
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def shift_right(self, count, in_place=True, **kwargs):
        """
        Convenience method for: shift-right

        :type count: int, The number of places to shift.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :param kwargs['default_value']: The default value to use.
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def sl(self, count, in_place=True, **kwargs):
        """
        Convenience method for: shift-left

        :see: shift_left
        """
        raise NotImplementedError()

    @abstractmethod
    def sr(self, count, in_place=True, **kwargs):
        """
        Convenience method for: shift-right

        :see: shift_right
        """
        raise NotImplementedError()


@add_metaclass(ABCMeta)
class wrap_api(base_api):  # pragma no cover
    @abstractmethod
    def wrap(self, count, in_place=True, direction=None):
        """
        wrap

        :type count: int, The number of places to wrap.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :type direction: one of [LEFT, RIGHT].
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def wrap_left(self, count, in_place=True):
        """
        Convenience method for: wrap-left

        :type count: int, The number of places to wrap.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def wrap_right(self, count, in_place=True):
        """
        Convenience method for: wrap-right

        :type count: int, The number of places to wrap.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def wl(self, count, in_place=True):
        """
        Convenience method for: wrap-left

        :see: wrap_leftif not hasattr(self, '_default_value'):
        """
        raise NotImplementedError()

    @abstractmethod
    def wr(self, count, in_place=True):
        """
        Convenience method for: wrap-right

        :see: wrap_right
        """
        raise NotImplementedError()


@add_metaclass(ABCMeta)
class helpers_api(base_api):  # pragma no cover
    @abstractmethod
    def set_items(self, items, indexes=None, in_place=False, **kwargs):
        """
        set items at given indexes

        :type items: iterable, The value to use during the set operation on the
            given index.
        :type indexes: iterable, The indexes of the items to set.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def clear_items(self, indexes=True, in_place=False, **kwargs):
        """
        clear items at given indexes

        :type indexes: iterable, The indexes of the items to set.
        :type in_place: bool, True - modify in-place, False - otherwise.
        :return: The modified iterable.
        """
        raise NotImplementedError()

    @abstractmethod
    def get(self, indexes=None, in_place=False, **kwargs):
        """
        get items at given indexes

        :type indexes: iterable, The indexes of the items to get.
        :return: The items at the given indexes.
        """
        raise NotImplementedError()

    @abstractmethod
    def iget(self, indexes=None, in_place=False, **kwargs):
        """
        iterator to get items at given indexes

        :type indexes: iterable, The indexes of the items to get.
        :return: The items at the given indexes.
        """
        raise NotImplementedError()

    @abstractmethod
    def xget(self, indexes=None, in_place=False, **kwargs):
        """
        get items not at given indexes

        :type indexes: iterable, The indexes of the items to get.
        :return: The items at the given indexes.
        """
        raise NotImplementedError()

    @abstractmethod
    def ixget(self, indexes=None, in_place=False, **kwargs):
        """
        iterator to get items not at given indexes

        :type indexes: iterable, The indexes of the items to get.
        :return: The items at the given indexes.
        """
        raise NotImplementedError()


if __name__ == '__main__':  # pragma no cover
    pass

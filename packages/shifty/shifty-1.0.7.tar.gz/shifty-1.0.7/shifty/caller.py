# -*- coding: utf-8 -*-
"""
wrapper for user callable. Allows a callable to be a valid list item.
"""

import copy
from abc import ABCMeta
from six import add_metaclass
from shifty.errors import CriticalError, CircularRef


@add_metaclass(ABCMeta)
class CallerData(object):
    def __init__(self, func):
        """
        param func: The callable to execute. If func is not callable, this
        value will be returned.
        """
        self._func = func

    @property
    def func(self):
        return self._func

    @property
    def is_callable(self):
        return callable(self.func)

    @property
    def iterable(self):
        return isinstance(self, Iter)

    @property
    def callable(self):
        return isinstance(self, Caller)

    @property
    def value(self):
        return CallerData.get_value(self)

    @staticmethod
    def get_value(item, context=None):
        """
        Convenience method to get the value of the callable (if callable).
        Warning, this method is recursive.

        :param item: The item to check.
        """

        def append_context(ctx_, item_):
            if id(item_) in [k[0] for k in ctx_] and isinstance(item_,
                                                                CallerData):
                raise CircularRef(item_)
            ctx_.append((id(item_), item_))

        context = context if context is not None else []
        if callable(item) and context and isinstance(context[-1][1], Caller):
            return item()

        if not isinstance(item, CallerData):
            return item

        func = item.func
        if item.callable:
            append_context(context, item)
            return CallerData.get_value(func, context)
        elif item.iterable:
            ctx = copy.copy(context)
            try:
                append_context(ctx, item)
                if isinstance(func, Iter):
                    return CallerData.get_value(func, ctx)
                else:
                    return [CallerData.get_value(i, ctx) for i in func]
            finally:
                ctx.pop(-1)
        raise CriticalError('Unable to handle CallerData: %s' % item)


class Iter(CallerData):
    """
    Wrapper to use for a iterable which should be explicitly called to
    evaluate a parameter, typically used as a Caller.func.

    Note: func WILL ALWAYS be accessed as an iterable OR Iter.
    """

    def __repr__(self):
        return 'Iter(%s)' % self.func


class Caller(CallerData):
    """
    Wrapper to use for a callable or iterable func which should be explicitly
    called to evaluate a parameter.
    Note: func will be evaluated by get_value (not necessarily a callable).
    """

    def __repr__(self):
        return 'User-Callable(%s)' % self.func


if __name__ == '__main__':  # pragma no cover
    pass

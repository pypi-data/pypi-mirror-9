# -*- coding: utf-8 -*-
"""
Shifty.
"""

__author__ = 'Francis Horsman'
__version__ = '1.0.7'
__url__ = 'https://bitbucket.org/sys-git/shifty'
__email__ = 'francis.horsman@gmail.com'
__short_description__ = 'A pure-python list shifter/wrapper'
__synopsis__ = '.\nWraps a list left or right by any amount ' \
               '(modulo to the length of list), or<n' \
               'Shifts a list left or right by any amount.' \
               'Can optionally shift/wrap the list in-place.' \
               'Create a shifty instance to add these convenience ' \
               'methods to the default list implementation ' \
               'if you prefer.\nIterators provided to iterate over' \
               'continual shifts/wraps over the entire list or an ' \
               'individual list\'s item at a constant index'
__long_description__ = __short_description__ + __synopsis__

LEFT = 'left'
RIGHT = 'right'
SET = 'set'
CLEAR = 'clear'
WRAP = 'wrap'
SHIFT = 'shift'
DEFAULT_VALUE = None

from shifty.caller import Caller  # NOQA
from shifty.errors import CriticalError  # NOQA
from shifty.impls import shifty  # NOQA
from shifty.iterators import ShiftyIterable, ShiftyWatcher, \
    ShiftyIndexWatcher  # NOQA
from shifty.wrappers import shift, shift_left, shift_right, sl, sr, wl, \
    wr, wrap, wrap_left, wrap_right  # NOQA

if __name__ == '__main__':  # pragma no cover
    pass

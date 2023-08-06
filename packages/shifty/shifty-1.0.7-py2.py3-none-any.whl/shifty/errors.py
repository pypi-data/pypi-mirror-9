# -*- coding: utf-8 -*-
"""
All custom exceptions.
"""


class CriticalError(ValueError):
    """
    A critical error (software bug) has been detected.
    """
    pass


class CircularRef(ValueError):
    """
    A circular reference is discovered in an instance of CallerData.
    """

    def __init__(self, item):
        ValueError.__init__(self, item)
        self.item = item


if __name__ == '__main__':  # pragma no cover
    pass

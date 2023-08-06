README
======

A pure-python list-shifter/wrapper. Shifts/Wraps an iterable left or
right by any amount (modulo to the length of iterable). Can optionally
shift the iterable in-place. Create a shifty instance to add these
convenience methods to the default list implementation if you prefer.

Why slice when you can shift 'like-a-boss' ?!


How do I get set up?
~~~~~~~~~~~~~~~~~~~~

-  **python setup.py install**
-  Dependencies: six
-  Dependencies (test): **Coverage, nose**
-  How to run tests: **./runtests.sh**
-  Deployment instructions: **pip install shifty**

Contribution guidelines
~~~~~~~~~~~~~~~~~~~~~~~

I accept pull requests.

What about test coverage?
~~~~~~~~~~~~~~~~~~~~~~~~~

There is a full suite of unit-tests.

Who do I talk to?
~~~~~~~~~~~~~~~~~

-  Francis Horsman: **francis.horsman@gmail.com**

Example
~~~~~~~

::

    >>> from shifty import shift_left, shifty

    >>> a = [1, 2, 3, 4]
    >>> b = shift_left(a, 3)
    >>> b
    [4, 1, 2, 3]
    >>> assert a is not b

    >>> b = shift_left(a, 2, in_place=True)

    >> assert a is b

    >>> b = shift_left(a, 5)

    >>> b
    [4, 1, 2, 3]


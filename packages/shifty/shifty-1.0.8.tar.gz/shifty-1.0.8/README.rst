README
======

A pure-python list-shifter/wrapper. Shifts/Wraps an iterable left or
right by any amount (modulo to the length of iterable). Can optionally
shift the iterable in-place. Create a shifty instance to add these
convenience methods to the default list implementation if you prefer.

Why slice when you can shift 'like-a-boss' ?!

.. image:: https://codeship.com/projects/3b9b4360-9a44-0132-7e10-0ee228cf83fe/status?branch=master
    :target: https://codeship.com/projects/63870
    :alt: Codeship Status
.. image:: https://api.shippable.com/projects/54afbe1ad46935d5fbc1e905/badge?branchName=master
    :target: https://app.shippable.com/projects/54afbe1ad46935d5fbc1e905/builds/latest
    :alt: Build Status
.. image:: https://pypip.in/download/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: Downloads
.. image:: https://pypip.in/version/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: Latest Version
.. image:: https://pypip.in/py_versions/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: Supported Python versions
.. image:: https://pypip.in/status/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: Development Status
.. image:: https://pypip.in/wheel/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: Wheel Status
.. image:: https://pypip.in/egg/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: Egg Status
.. image:: https://pypip.in/format/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: Download format
.. image:: https://pypip.in/license/shifty/badge.svg
    :target: https://pypi.python.org/pypi/shifty/
    :alt: License

How do I get set up?
~~~~~~~~~~~~~~~~~~~~

-  **python setup.py install**
-  Dependencies: **six**
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


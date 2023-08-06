=============
mutabletuple
=============

Overview
========

Similar to namedlist, but with additional features:
* Print like a native python dictionary
* Improve support for nested mutabletuple
* Conversion to dictionary is done recursively
* Can iterate using iteritems like dictionary
* Merge nested mutable tuple from dict or other mutabletuple
* MtFactory support arguments
* Nested pickle support

**Warning** Pickling works, but only for mutabletuple with default values.

Typical usage
=============

You can use mutabletuple like a mutable namedtuple::

    >>> from mutabletuple import mutabletuple
    >>> from collections import OrderedDict

    >>> Point = mutabletuple('Point', 'x y')
    >>> p = Point(1, 3)
    >>> p.x = 2
    >>> assert p.x == 2
    >>> assert p.y == 3

Or, you can specify a default value for all fields::

    >>> Point = mutabletuple('Point', ['x', 'y'], default=3)
    >>> p = Point(y=2)
    >>> assert p.x == 3
    >>> assert p.y == 2

Or, you can specify per-field default values::

    >>> Point = mutabletuple('Point', [('x', 0), ('y', 100)])
    >>> p = Point()
    >>> assert p.x == 0
    >>> assert p.y == 100

If you use a mapping, the value MtNoDefault is convenient to specify
that a field uses the default value::

    >>> from mutabletuple import MtNoDefault
    >>> Point = mutabletuple('Point', OrderedDict((('y', MtNoDefault),
    ...                                            ('x', 100))),
    ...                                            default=5)
    >>> p = Point()
    >>> assert p.x == 100
    >>> assert p.y == 5

Namedlist-like behavior
=======================

A mutabletuple behaves almost like a namedlist. Check the documentation of namedlist for more details: https://pypi.python.org/pypi/namedlist

Additional features
===================

Additional class members
------------------------

mutabletuple class contain these members:

* _asdict(): Returns a dict which maps field names to their
  corresponding values.

* _fields: Tuple of strings listing the field names. Useful for introspection.

* merge: Recursively merge with a dict or another mutabletuple.

* orderedDict: Recursively convert a mutabletuple into an ordered dict.

* iteritems: To iterate like a dict.


Mutable default values
----------------------

For mutabletuple, be aware of specifying mutable default
values. Due to the way Python handles default values, each instance of
a mutabletuple will share the default. This is especially problematic
with default values that are lists. For example::

    >>> A = mutabletuple('A', [('x', [])])
    >>> a = A()
    >>> a.x.append(4)
    >>> b = A()
    >>> assert b.x == [4]

This is probably not the desired behavior, so see the next section.


Specifying a factory function for default values
------------------------------------------------

For mutabletuple, you can supply a zero-argument callable for a
default, by wrapping it in a MtFactory call. The only change in this
example is to change the default from `[]` to `MtFactory(list)`. But
note that `b.x` is a new list object, not shared with `a.x`::

    >>> from mutabletuple import MtFactory
    >>> A = mutabletuple('A', [('x', MtFactory(list))])
    >>> a = A()
    >>> a.x.append(4)
    >>> b = A()
    >>> assert b.x == []

Every time a new instance is created, your callable (in this case,
`list`), will be called to produce a new instance for the default
value.

Specifying arguments to a factory function
------------------------------------------

When using nested mutabletuple, you might want to provide arguments
for the creation of nested mutabletuple. Here is an example of
how to do it::

    >>> Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
    >>> Vector = mutabletuple('Vector', [('p1', MtFactory(Point, 2)),
    ...                                  ('p2', MtFactory(Point, 4, 8))])
    >>> v1     = Vector()
    >>> assert(v1 == Vector(Point(2, 0), Point(4, 8)))

Initialized points are created every time a vector is created.


Merging mutabletuple with mutabletuple or dict
----------------------------------------------

When working with nested mutabletuple, it might be useful to be able
to merge recursively with a dictionary that represents only a subset
of the mutabletuple::

    >>> Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
    >>> Vector = mutabletuple('Vector', [('p1', MtFactory(Point)),
    ...                                  ('p2', MtFactory(Point))])
    >>> Shape  = mutabletuple('Shape', [('v1', MtFactory(Vector)),
    ...                                 ('v2', MtFactory(Vector))])
    >>> s = Shape()
    >>> d = {'v1': {'p1': {'x': 20}, 'p2': Point(30, 40)}}
    >>> s.merge(d)
    >>> assert(s._asdict() == {
    ...     'v1': {'p1': {'x': 20, 'y': 0}, 'p2': {'x': 30, 'y': 40}},
    ...     'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}})


Iterating over instances
------------------------

Because instances are iterable (like lists or tuples), iteration works
the same way. Values are returned in definition order::

    >>> Point = mutabletuple('Point', 'x y z t')
    >>> p = Point(1.0, 42.0, 3.14, 2.71828)
    >>> for value in p:
    ...    print(value)
    1.0
    42.0
    3.14
    2.71828

Creating and using instances
============================

Because the type returned by mutabletuple is a normal
Python class, you create instances as you would with any Python class.


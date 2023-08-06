"""Similar to namedlist, but with additional features.

@author       : Nicolas BESSOU <nicolas.bessou@gmail.com>
@copyright    : Copyright 2015, Nicolas BESSOU
"""

import namedlist
from collections import OrderedDict

__all__ = ['mutabletuple', 'ismutabletuple', 'MtNoDefault', 'MtFactory']

# *****************************************************************************
# namedtuple utilities
# *****************************************************************************
MtNoDefault = namedlist.NO_DEFAULT


class MtFactory(namedlist.FACTORY):

    """Wrapper around a callable. Used to specify a factory function instead of a plain default value."""

    def __init__(self, callable, *args, **kwargs):
        self._callable = callable
        self.args = args
        self.kwargs = kwargs

    def call(self):
        return self._callable(*self.args, **self.kwargs)

    def __repr__(self):
        return '{0!r}'.format(self.call())


# *****************************************************************************
# Member functions that extends namedlist functionality
# *****************************************************************************
def _mt_repr(self):
    """Print mutable tuple like dict."""
    return '{{{0}}}'.format(', '.join('\'{0}\': {1!r}'.format(name, getattr(self, name)) for name in self._fields))


def _mt_asdict(self):
    """Recursively convert mutabletuple to a dict."""
    newdict = {}
    for key in self._fields:
        value = getattr(self, key)
        if ismutabletuple(value):
            newdict[key] = value._asdict()
        else:
            newdict[key] = value
    return newdict


def _mt_orderedDict(self):
    """Recursively convert mutabletuple to an ordered dict."""
    newdict = OrderedDict()
    for key in self._fields:
        value = getattr(self, key)
        if ismutabletuple(value):
            newdict[key] = value.orderedDict()
        else:
            newdict[key] = value
    return newdict


def _mt_iteritems(self):
    """Iterate like dict."""
    for key in self._fields:
        yield (key, getattr(self, key))


def _mt_merge(self, container):
    """Recursively merge current mutabletuple with another mutabletuple or dictionary."""
    if not hasattr(container, 'iteritems'):
        raise TypeError('Cannot merge with given type {}'.format(type(container)))

    for (key, value) in container.iteritems():
        if isinstance(value, dict):
            _mt_merge(getattr(self, key), value)
        elif ismutabletuple(value):
            getattr(self, key).merge(value)
        else:
            if isinstance(self, dict):
                self[key] = value
            else:
                setattr(self, key, value)


def _mt_init(self, *args):
    """Initialize a namedtuple with fields, default values and factory."""
    # Get values and call factory when required.
    assert len(self._fields) == len(args)
    values = [(fieldname, (value.call() if isinstance(value, MtFactory) else value)) for fieldname, value in zip(self._fields, args)]

    # sets all of the fields to their passed in values
    for fieldname, value in values:
        setattr(self, fieldname, value)


def _mt_getstate(self):
    return self._asdict()


def _mt_setstate(self, state):
    # We have to call init without argument because we don't want
    # to overwrite the type of every field.
    # Therefore, pickling only works for mutabletuple with default values
    self.__init__()
    self.merge(state)


# *****************************************************************************
# Interface functions
# *****************************************************************************
def ismutabletuple(element):
    """Check if element is of type mutabletuple."""
    return True if hasattr(element, 'MutableTupleUniqueIdentifier') else False


def mutabletuple(typename, field_names, default=MtNoDefault):
    """Factory function that creates a class mutabletuple."""
    # Create a namedlist
    mtuple = namedlist.namedlist(typename, field_names, default)

    # Set unique attribute to identify mutabletuple classes
    mtuple.MutableTupleUniqueIdentifier = None

    # Extend namedlist functionality
    (fields, defaults)     = namedlist._fields_and_defaults(typename, field_names, default, rename=False)
    mtuple.__init__        = namedlist._make_fn('__init__', _mt_init, fields, defaults)
    mtuple.__repr__        = _mt_repr
    mtuple._asdict         = _mt_asdict
    mtuple.iteritems       = _mt_iteritems
    mtuple.merge           = _mt_merge
    mtuple.orderedDict     = _mt_orderedDict
    mtuple.__getstate__    = _mt_getstate
    mtuple.__setstate__    = _mt_setstate

    # Assign the class as a global under the same name
    # Required for pickle so the class seems declared at global level.
    globals()[typename] = mtuple

    return mtuple

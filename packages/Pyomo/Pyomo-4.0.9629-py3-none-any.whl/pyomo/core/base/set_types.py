#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

__all__ = [
  '_VirtualSet', '_AnySet', 'RealSet', 'IntegerSet', 'BooleanSet', 'Any',
  'AnyWithNone', 'Reals', 'PositiveReals', 'NonPositiveReals', 'NegativeReals',
  'NonNegativeReals', 'PercentFraction', 'UnitInterval', 'Integers', 'PositiveIntegers',
  'NonPositiveIntegers', 'NegativeIntegers', 'NonNegativeIntegers', 'Boolean',
  'Binary', 'RealInterval', 'IntegerInterval'
]

import sys
import weakref
from six import iteritems

import pyomo.util.plugin

from pyomo.core.base.sets import SimpleSet
from pyomo.core.base.numvalue import native_numeric_types, \
    native_integer_types, native_boolean_types
from pyomo.core.base.plugin import *

_virtual_sets = []


class _VirtualSet(SimpleSet, pyomo.util.plugin.Plugin):
    """
    A set that does not contain elements, but instead overrides the
       __contains__ method to define set membership.
    """

    pyomo.util.plugin.implements(IPyomoSet)

    def __init__(self,*args,**kwds):
        if "name" in kwds:
            pyomo.util.plugin.Plugin.__init__(self,name=kwds["name"])
        else:
            pyomo.util.plugin.Plugin.__init__(self)
        self._class_override=False
        SimpleSet.__init__(self, *args, **kwds)
        self.virtual=True
        self.concrete=False
        
        global _virtual_sets
        _virtual_sets.append(self)

    def data(self):
        raise TypeError("Cannot access data for a virtual set")


class _AnySet(_VirtualSet):
    """A virtual set that allows any value"""

    def __init__(self,*args,**kwds):
        """Constructor"""
        _VirtualSet.__init__(self,*args,**kwds)

    def __contains__(self, element):
        if element is None:
            return False
        return True


class _AnySetWithNone(_AnySet):
    """A virtual set that allows any value (including None)"""

    def __contains__(self, element):
        return True


class RealSet(_VirtualSet):
    """A virtual set that represents real values"""

    def __init__(self,*args,**kwds):
        """Constructor"""
        if not 'bounds' in kwds:
            kwds['bounds'] = (None,None)
        _VirtualSet.__init__(self,*args,**kwds)

    def __contains__(self, element):
        """Report whether an element is an 'int', 'long' or 'float' value.

        (Called in response to the expression 'element in self'.)
        """
        return _VirtualSet.__contains__(self, element) and \
            ( element.__class__ in native_numeric_types )


class IntegerSet(_VirtualSet):
    """A virtual set that represents integer values"""

    def __init__(self,*args,**kwds):
        """Constructor"""
        if not 'bounds' in kwds:
            kwds['bounds'] = (None,None)
        _VirtualSet.__init__(self,*args,**kwds)

    def __contains__(self, element):
        """Report whether an element is an 'int'.

        (Called in response to the expression 'element in self'.)
        """
        return _VirtualSet.__contains__(self, element) and \
            ( element.__class__ in native_integer_types )


class BooleanSet(_VirtualSet):
    """A virtual set that represents boolean values"""

    def __init__(self,*args,**kwds):
        """Construct the set of booleans, which contains no explicit values"""
        kwds['bounds'] = (0,1)
        _VirtualSet.__init__(self,*args,**kwds)

    def __contains__(self, element):
        """Report whether an element is a boolean.

        (Called in response to the expression 'element in self'.)
        """
        return _VirtualSet.__contains__(self, element) \
               and ( element.__class__ in native_boolean_types ) \
               and ( element in (0, 1, True, False, 'True', 'False', 'T', 'F') )


class RealInterval(RealSet):
    """A virtual set that represents an interval of real values"""

    def __init__(self, *args, **kwds):
        """Constructor"""
        if not 'bounds' in kwds:
            kwds['bounds'] = (None,None)
        _bounds = kwds['bounds']
        def validate_interval(model,x): return (_bounds[0] is None or x >= _bounds[0]) and (_bounds[1] is None or x <= _bounds[1])
        kwds['validate'] = validate_interval
        RealSet.__init__(self, *args, **kwds)


class IntegerInterval(IntegerSet):
    """A virtual set that represents an interval of integer values"""

    def __init__(self, *args, **kwds):
        """Constructor"""
        if not 'bounds' in kwds:
            kwds['bounds'] = (None,None)
        _bounds = kwds['bounds']
        def validate_interval(model,x): return (_bounds[0] is None or x >= _bounds[0]) and (_bounds[1] is None or x <= _bounds[1])
        kwds['validate'] = validate_interval
        IntegerSet.__init__(self, *args, **kwds)


#
# Concrete instances of the standard sets
#
Any=_AnySet(name="Any", doc="A set of any data")
AnyWithNone=_AnySetWithNone(name="AnyWithNone", doc="A set of any data (including None)")

Reals=RealSet(name="Reals", doc="A set of real values")
def validate_PositiveValues(model,x):    return x >  0
def validate_NonPositiveValues(model,x): return x <= 0
def validate_NegativeValues(model,x):    return x <  0
def validate_NonNegativeValues(model,x): return x >= 0
def validate_PercentFraction(model,x):   return x >= 0 and x <= 1.0

PositiveReals    = RealSet(
  name="PositiveReals",
  validate=validate_PositiveValues,
  doc="A set of positive real values",
  bounds=(0, None)
)
NonPositiveReals = RealSet(
  name="NonPositiveReals",
  validate=validate_NonPositiveValues,
  doc="A set of non-positive real values",
  bounds=(None, 0)
)
NegativeReals    = RealSet(
  name="NegativeReals",
  validate=validate_NegativeValues,
  doc="A set of negative real values",
  bounds=(None, 0)
)
NonNegativeReals = RealSet(
  name="NonNegativeReals",
  validate=validate_NonNegativeValues,
  doc="A set of non-negative real values",
  bounds=(0, None)
)

PercentFraction = RealSet(
  name="PercentFraction",
  validate=validate_PercentFraction,
  doc="A set of real values in the interval [0,1]",
  bounds=(0.0,1.0)
)

UnitInterval = PercentFraction

Integers            = IntegerSet(
  name="Integers",
  doc="A set of integer values"
)
PositiveIntegers    = IntegerSet(
  name="PositiveIntegers",
  validate=validate_PositiveValues,
  doc="A set of positive integer values",
  bounds=(1, None)
)
NonPositiveIntegers = IntegerSet(
  name="NonPositiveIntegers",
  validate=validate_NonPositiveValues,
  doc="A set of non-positive integer values",
  bounds=(None, 0)
)
NegativeIntegers    = IntegerSet(
  name="NegativeIntegers",
  validate=validate_NegativeValues,
  doc="A set of negative integer values",
  bounds=(None, -1)
)
NonNegativeIntegers = IntegerSet(
  name="NonNegativeIntegers",
  validate=validate_NonNegativeValues,
  doc="A set of non-negative integer values",
  bounds=(0, None)
)

Boolean = BooleanSet( name="Boolean", doc="A set of boolean values")
Binary  = BooleanSet( name="Binary",  doc="A set of boolean values")

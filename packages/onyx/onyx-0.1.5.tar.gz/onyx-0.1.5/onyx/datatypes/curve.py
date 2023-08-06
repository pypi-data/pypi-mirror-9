###############################################################################
#
#   Onyx Portfolio & Risk Management Framework
#
#   Copyright 2014 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.datatypes.gcurve import GKnot, GCurve

import numpy as np
import bisect

__all__ = ["Knot", "Curve"]


##-----------------------------------------------------------------------------
def is_numlike(obj):
    """
    Helper function used to determine if an object looks like a number.
    """
    try:
        obj + 1
    except:
        return False
    else:
        return True


###############################################################################
class Knot(GKnot):
    """
    Class representing a curve knot as a pair (date, value) where value is
    stored as a float datatype.
    """
    __slots__ = ("date", "value")

    ##-------------------------------------------------------------------------
    def __init__(self, d, v):
        self.date = d
        self.value = float(v)

    ##-------------------------------------------------------------------------
    def __str__(self):
        return "{0!s}, {1:17.8f}".format(self.date, self.value)


###############################################################################
class Curve(GCurve):
    """
    Curve class (based on Knot class, which only stores numeric values)
    """
    __slots__ = ("data", "knot_cls")

    ##-------------------------------------------------------------------------
    def __init__(self, dates=None, values=None, knot_cls=None):
        """
        Description:
            Create a curve from dates and numeric values. Raise a CurveError
            exception if dates contains any duplicates.
        Inputs:
            dates    - list/array of Dates
            values   - list/array of values (values must be castable to float)
            knot_cls - optional, the Knot constructor
        """
        knot_cls = knot_cls or Knot
        super().__init__(dates, values, knot_cls)

    ##-------------------------------------------------------------------------
    @property
    def values(self):
        return np.fromiter((knot.value for knot in self.data),
                           dtype=float, count=len(self.data))

    ##-------------------------------------------------------------------------
    def __getitem__(self, d):
        """
        Reimplement __getitem__ using linear interpolation.
        """
        dts = self.dates
        idx = bisect.bisect_left(dts, d)

        if d >= dts[0] and d <= dts[-1] and dts[idx] == d:
            return self.data[idx].value
        else:
            # --- use linear interpolation
            if idx == 0:
                return self.data[0].value
            elif idx == len(dts):
                return self.data[-1].value
            else:
                frc = ((d.ordinal - dts[idx-1].ordinal) /
                       (dts[idx].ordinal - dts[idx-1].ordinal))
                cfrc = 1.0 - frc
                return (cfrc*self.data[idx-1].value + frc*self.data[idx].value)

    ##-------------------------------------------------------------------------
    ##  A few methods for simple curve algebra. It's always assumed that the
    ##  two curves are correctly aligned

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.dates, self.values + other.values)
        else:
            return self.__class__(self.dates, self.values + other)

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.dates, self.values - other.values)
        else:
            return self.__class__(self.dates, self.values - other)

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.dates, self.values * other.values)
        elif is_numlike(other):
            return self.__class__(self.dates, self.values * other)
        else:
            TypeError("cannot multiply a {0:s} "
                      "by a {1:s}".format(self.__class__, other.__class__))

    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.dates, self.values / other.values)
        elif is_numlike(other):
            return self.__class__(self.dates, self.values / other)
        else:
            TypeError("cannot multiply a {0:s} "
                      "by a {1:s}".format(self.__class__, other.__class__))

    def __radd__(self, scalar):
        return self.__class__(self.dates, scalar + self.values)

    def __rsub__(self, scalar):
        return self.__class__(self.dates, scalar - self.values)

    def __rmul__(self, scalar):
        return self.__class__(self.dates, scalar * self.values)

    def __rtruediv__(self, scalar):
        return self.__class__(self.dates, scalar / self.values)

    ##-------------------------------------------------------------------------
    def crop_values(self, start=None, end=None):
        """
        Description:
            Return an array of values that fall within the specified range.
            If start date or end date are not set, use the current extremes of
            the curve.
        Inputs:
            start - the start of the range (included)
            end   - the   end of the range (included)
        Returns:
            An array of values within the range.
        """
        # --- store dates in local variable for faster access
        dts = self.dates

        # --- set the two extremes of the range
        start = start or dts[0]
        end = end or dts[-1]

        i = bisect.bisect_left(dts, start)
        j = bisect.bisect_right(dts, end, i)

        return self.values[i:j]

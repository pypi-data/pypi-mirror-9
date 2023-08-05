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

import numpy as np
import collections
import bisect

__all__ = ["GKnot", "GCurve", "KnotError", "CurveError"]


###############################################################################
class KnotError(Exception):
    """
    Base class for all Knot exceptions.
    """
    pass


###############################################################################
class CurveError(Exception):
    """
    Base class for all Curve exceptions.
    """
    pass


###############################################################################
class GKnot(object):
    """
    Class representing a generic curve knot as a pair (date, value).
    """
    __slots__ = ("date", "value")

    ##-------------------------------------------------------------------------
    def __init__(self, d, v):
        self.date = d
        self.value = v

    ##-------------------------------------------------------------------------
    ##  support serialization

    def __getstate__(self):
        return (self.date, self.value)

    def __setstate__(self, state):
        self.date, self.value = state

    ##-------------------------------------------------------------------------
    def __repr__(self):
        cls = self.__class__
        return "{.__name__:s}({.date!r},{.value!r})".format(cls, self, self)

    ##-------------------------------------------------------------------------
    def __str__(self):
        return "{0!s}, unprintable value...".format(self.date)

    ##-------------------------------------------------------------------------
    ##  methods for knot comparison (date based)

    def __lt__(self, other):
        return self.date < other.date

    def __le__(self, other):
        return self.date <= other.date

    def __gt__(self, other):
        return self.date > other.date

    def __ge__(self, other):
        return self.date >= other.date

    ##-------------------------------------------------------------------------
    ##  quality/inquality are based on both date and value

    def __eq__(self, other):
        return self.date == other.date and self.value == other.value

    def __ne__(self, other):
        return self.date != other.date or self.value != other.value


###############################################################################
class GCurve(object):
    """
    Base Curve class (based on GKnot class).
    """
    __slots__ = ("data", "knot_cls")

    ##-------------------------------------------------------------------------
    def __init__(self, dates=None, values=None, knot_cls=None):
        """
        Description:
            Create a curve from dates and generic values. Raise a CurveError
            exception if dates contains any duplicates.
        Inputs:
            dates    - list/array of Dates
            values   - list/array of values
            knot_cls - optional Knot constructor
        """
        if dates is None: dates = []    # analysis:ignore
        if values is None: values = []  # analysis:ignore

        if len(dates) != len(values):
            raise CurveError("Input dates and values are of different length")

        self.knot_cls = knot_cls or GKnot

        # --- check if creating an empty curve
        if not len(dates):
            self.data = []
        else:
            # --- check whether there are any duplicates in dates
            if len(dates) != len(set(dates)):
                # --- raise exception with list of duplicates
                duplicates = {x: y for x, y
                              in collections.Counter(dates).items() if y > 1}
                raise CurveError("Creating curve with duplicate "
                                 "dates: {0:s}".format(duplicates.__repr__()))

            # --- the curve is stored internally as a list of knots
            self.data = [self.knot_cls(d, v) for (d, v) in zip(dates, values)]
            # --- sort the curve by dates (natural ordering of knots)
            self.data.sort()

    ##-------------------------------------------------------------------------
    ##  methods for curve comparison

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self.data[i] != other.data[i]:
                return False
        return True

    def __ne__(self, other):
        if len(self) != len(other):
            return True
        for i in range(len(self)):
            if self.data[i] != other.data[i]:
                return True
        return False

    ##-------------------------------------------------------------------------
    def sort(self, *args, **kwds):
        self.data.sort(*args, **kwds)

    ##-------------------------------------------------------------------------
    ##  support serialization

    def __getstate__(self):
        return self.knot_cls, self.data

    def __setstate__(self, state):
        self.knot_cls, self.data = state

    ##-------------------------------------------------------------------------
    ##  string representation

    def __repr__(self):
        cls = self.__class__.__name__
        dts = self.dates
        vls = list(self.values)
        return "{0:s}(dates={1!r}, values={2!r})".format(cls, dts, vls)

    def __str__(self):
        return "\n".join([knot.__str__() for knot in self.data])

    ##-------------------------------------------------------------------------
    def has_knot(self, d):
        """
        Description:
            Check whether a knot for a given date is present.
        Inputs:
            d - the knot date
        Returns:
            True if knot is present, False otherwise.
        """
        dts = self.dates
        if not len(dts):
            return False
        if d < dts[0] or d > dts[-1]:
            return False
        idx = bisect.bisect_left(dts, d)
        if dts[idx] == d:
            return True
        else:
            return False

    ##-------------------------------------------------------------------------
    def get_knot(self, d):
        """
        Description:
            Return the knot for a given date if present. Raise IndexError
            exception otherwise.
        Inputs:
            d - the knot date
        Returns:
            The curve's knot.
        """
        dts = self.dates
        idx = bisect.bisect_left(dts, d)
        try:
            if dts[idx] == d:
                return self.data[idx]
            else:
                raise IndexError
        except:
            raise IndexError

    ##-------------------------------------------------------------------------
    def add_knot(self, knot):
        """
        Description:
            Add a knot in-place to the curve preserving order.
        Inputs:
            Knot - the knot to be added to the curve
        Returns:
            None.
        """
        bisect.insort(self.data, knot)

    ##-------------------------------------------------------------------------
    def del_knot(self, d):
        """
        Description:
            Delete in-place the knot corresponding to a given date if the knot
            is present. Raise IndexError exception otherwise.
        Inputs:
            d - the knot date
        Returns:
            None.
        """
        dts = self.dates
        idx = bisect.bisect_left(dts, d)
        try:
            if dts[idx] == d:
                self.data.pop(idx)
            else:
                raise IndexError
        except:
            raise IndexError

    ##-------------------------------------------------------------------------
    ##  GCurve is an iterable object: implement all relevant methods

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, d):
        dts = self.dates
        idx = bisect.bisect_left(dts, d)

        if d >= dts[0] and d <= dts[-1] and dts[idx] == d:
            return self.data[idx].value
        else:
            # --- use step interpolation (previous knot)
            if idx:
                return self.data[idx-1].value
            else:
                return self.data[0].value

    def __setitem__(self, d, v):
        try:
            idx = self.dates.index(d)
            self.data[idx].value = v
        except ValueError:
            bisect.insort(self.data, self.knot_cls(d, v))

    ##-------------------------------------------------------------------------
    def append(self, knot):
        """
        Append new knot (assuming it's already in the correct position).
        """
        self.data.append(knot)

    ##-------------------------------------------------------------------------
    @property
    def ordinals(self):
        """
        Return an array with curve dates in numeric format.
        """
        return np.fromiter((knot.date.ordinal for knot in self.data),
                           dtype=float, count=len(self.data))

    ##-------------------------------------------------------------------------
    @property
    def dates(self):
        """
        Return a list with curve dates in Date format.
        """
        return [knot.date for knot in self.data]

    ##-------------------------------------------------------------------------
    @property
    def values(self):
        """
        Return a list with curve's knot values.
        """
        return [knot.value for knot in self.data]

    ##-------------------------------------------------------------------------
    @property
    def front(self):
        """
        Description:
            Return the first knot of the curve.
        Returns:
            A knot.
        """
        return self.data[0]

    @property
    def back(self):
        """
        Description:
            Return the last knot of the curve.
        Returns:
            A knot.
        """
        return self.data[-1]

    ##-------------------------------------------------------------------------
    def crop(self, start=None, end=None):
        """
        Description:
            Return a sub-curve with knots that fall within the specified range.
            If start date or end date are not set, use the current extremes of
            the curve.
        Inputs:
            start - the start of the range (included)
            end   - the   end of the range (included)
        Return:
            A sub-curve of the original curve.
        """
        # --- store dates in local variable for faster access
        dts = self.dates

        # --- set the two extremes of the range
        start = start or dts[0]
        end = end or dts[-1]

        i = bisect.bisect_left(dts, start)
        j = bisect.bisect_right(dts, end, i)

        return self.__class__(dts[i:j], self.values[i:j])

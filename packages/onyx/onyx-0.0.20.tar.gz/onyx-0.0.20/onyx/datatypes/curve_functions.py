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

from onyx.datatypes.curve import Curve
from onyx.datatypes.gcurve import CurveError
from onyx.datatypes.rdate import RDate
from onyx.datatypes.date_functions import DateRange

import numpy as np
import bisect
import collections

__all__ = [
    "CurveShift",
    "CurveIntersect",
    "CurveUnion",
    "Interpolate",
    "ApplyToCurves",
    "CumSum",
    "Daily",
    "Weekly",
    "Monthly",
    "Quarterly",
    "Yearly",
]


##-----------------------------------------------------------------------------
def CurveShift(crv, rule, calendar=None):
    """
    Description:
        Apply the specified date rule to the each knot in the curve to obtain
        a new shifted curve.
        For a list of valid rules, see the RDate module.
    Inputs:
        crv      - the input curve
        rule     - the date-rule
        calendar - a holiday calendar used to identify business days
    Returns:
        The shifted curve.
    """
    cls = crv.knot_cls
    rdt = RDate(rule, calendar)
    shifted_dts = [d + rdt for d in crv.dates]
    shifted_crv = crv.__class__.__new__(crv.__class__)
    shifted_crv.data = [cls(*args)
                        for args in zip(shifted_dts, crv.values)]

    return shifted_crv


##-----------------------------------------------------------------------------
def CurveIntersect(curves):
    """
    Description:
        Intersect a list of curves returning a new list of curves with only
        the common knots presents.
    Inputs:
        curves - the list of curves to be intersected
    Returns:
        A list of curves with common knots.
    """
    # --- first find dates common to all curves
    common_dts = set(curves[0].dates)
    for k in range(1, len(curves)):
        common_dts.intersection_update(curves[k].dates)

    # --- then use these dates to build a list of curves with common knots
    new_curves = []
    for crv in curves:
        new_crv = crv.__class__.__new__(crv.__class__)
        new_crv.data = [knot for knot in crv.data if knot.date in common_dts]
        new_curves.append(new_crv)

    return new_curves


##-----------------------------------------------------------------------------
def CurveUnion(crv1, crv2):
    """
    Description:
        Return a curve formed by the union of knots from the two input
        curves. If common knots are present, those from the first curve
        will be used.
    Inputs:
        crv1 - the first  curve (takes precedence)
        crv2 - the second curve
    Returns:
        A new curve with the union of knots.
    """
    if type(crv1) != type(crv2):
        raise CurveError("CurveUnion: curves must be of the same "
                         "type: {0:s} - {1:s}".format(type(crv1), type(crv2)))

    # --- create auxiliary dictionaries
    d1 = dict(zip(crv1.dates, crv1.values))
    d2 = dict(zip(crv2.dates, crv2.values))

    # --- merge the two dictionaries giving priority to d1
    d2.update(d1)

    # --- NB: the curve constructor sorts knots by date automatically
    return crv1.__class__(d2.keys(), d2.values())


##-----------------------------------------------------------------------------
def Interpolate(crv, d, method="InterpolateStep"):
    """
    Description:
        Return the value at curve knot using the required interpolation scheme.
    Inputs:
        crv    - the curve
        d      - the knot date (a Date)
        method - interpolation scheme. Choose among:
                    "InterpolateStep":  return previous knot
    Returns:
        The curve knot's value.
    """
    try:
        # --- first try returning the knot (if knot is missing an IndexError
        #     will be raised by get_knot)
        return crv.get_knot(d).value
    except IndexError:
        if method == "InterpolateStep":
            idx = bisect.bisect_left(crv.dates, d)
            if idx:
                return crv.data[idx-1].value
            else:
                return crv.data[0].value
        else:
            raise NameError("Interpolate: unrecognized "
                            "interpolation method:{0:s}".format(method))


##-----------------------------------------------------------------------------
def CumSum(crv):
    """
    Description:
        Compute the cumulative sum of the curve values.
    Inputs:
        crv - the input curve
    Returns:
        A new curve with the cumulative sum.
    """
    if not isinstance(crv, Curve):
        raise TypeError("Cumulative sum is only available "
                        "for Curve objects, not for {0:s}".format(type(crv)))

    return Curve(crv.dates, np.cumsum(crv.values))


##-----------------------------------------------------------------------------
def ApplyToCurves(curves, func=min):
    """
    Description:
        Create a new curve appling a given function to the common knots of a
        list of curves.
    Inputs:
        curves - a list of curves
        func   - the function applied to the common knots (such as min, max,
                 mean, median, etc)
    Returns:
        A new curve where every common knot has value given by func(values)
        where values are for the same date.
    """
    curves = CurveIntersect(curves)

    crv = curves.pop()
    vls = [[v] for v in crv.values]

    for crv in curves:
        for k, v in enumerate(crv.values):
            vls.append(v)

    return Curve(crv.dates, [func(v) for v in vls])


##-----------------------------------------------------------------------------
def Daily(crv, method="InterpolateStep", calendar=None):
    """
    Description:
        Return a daily (business days) curve obtained by up-sampling via
        interpolation/extrapolation.
    Inputs:
        crv      - the input curve
        method   - interpolation method
        calendar - a holiday calendar used to identify business days
    Returns:
        A new curve with daily knots.
    """
    drange = DateRange(crv.front.date, crv.back.date, "+1b", calendar)
    knots = np.array([(d, Interpolate(crv, d, method)) for d in drange])
    return crv.__class__(knots[:,0], knots[:,1])


##-----------------------------------------------------------------------------
def Weekly(crv):
    """
    Description:
        Return a weekly averaged curve. Weekly values are set on Mondays.
    Inputs:
        crv - the input curve
    Returns:
        A new curve with weekly knots.
    """
    rd = RDate("+7d")
    d0 = crv.front.date + RDate("-1M")
    d1 = d0 + rd
    avg = collections.defaultdict(list)
    for knot in crv:
        while True:
            if knot.date < d1:
                avg[d0].append(knot.value)
                break
            else:
                d0 = d1
                d1 = d0 + rd

    return Curve(avg.keys(), [np.mean(v) for v in avg.values()])


##-----------------------------------------------------------------------------
def Monthly(crv):
    """
    Description:
        Return a monthly averaged curve. Monthly values are set on the first
        day of the month.
    Inputs:
        crv - the input curve
    Returns:
        A new curve with monthly knots.
    """
    rd = RDate("+1m")
    d0 = crv.front.date + RDate("+0J")
    d1 = d0 + rd
    avg = collections.defaultdict(list)
    for knot in crv:
        while True:
            if knot.Date < d1:
                avg[d0].append(knot.value)
                break
            else:
                d0 = d1
                d1 = d0 + rd

    return Curve(avg.keys(), [np.mean(v) for v in avg.values()])


##-----------------------------------------------------------------------------
def Quarterly(crv):
    """
    Description:
        Return a quarterly averaged curve. Quarterly average values are set on
        the first day of the quarter.
    Inputs:
        crv - the input curve
    Returns:
        A new curve with quarterly knots.
    """
    rd = RDate("+Q+1d")
    d0 = crv.front.date + RDate("+q")
    d1 = d0 + rd
    avg = collections.defaultdict(list)
    for knot in crv:
        while True:
            if knot.Date < d1:
                avg[d0].append(knot.value)
                break
            else:
                d0 = d1
                d1 = d0 + rd

    return Curve(avg.keys(), [np.mean(v) for v in avg.values()])


##-----------------------------------------------------------------------------
def Yearly(crv):
    """
    Description:
        Return a yearly averaged curve. Year average values are set on the
        first day of the year.
    Inputs:
        crv - the input curve
    Returns:
        A new curve with yearly knots.
    """
    rd = RDate("+E+1d")
    d0 = crv.front.date + RDate("+A")
    d1 = d0 + rd
    avg = collections.defaultdict(list)
    for knot in crv:
        while True:
            if knot.Date < d1:
                avg[d0].append(knot.value)
                break
            else:
                d0 = d1
                d1 = d0 + rd

    return Curve(avg.keys(), [np.mean(v) for v in avg.values()])

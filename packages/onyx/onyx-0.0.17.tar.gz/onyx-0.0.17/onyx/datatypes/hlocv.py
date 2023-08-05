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

from onyx.datatypes.gcurve import GKnot, GCurve, KnotError, CurveError
from onyx.datatypes.curve import Curve

import numpy as np

__all__ = ["HlocvKnot", "HlocvCurve", "HlocvKnotError", "HlocvCurveError"]


##-----------------------------------------------------------------------------
class HlocvKnotError(KnotError):
    pass


##-----------------------------------------------------------------------------
class HlocvCurveError(CurveError):
    pass


###############################################################################
class HlocvKnot(GKnot):
    """
    Class representing a HLOCV knot. Used for daily stock prices. It inherits
    from GKnot.
    """
    __slots__ = ("date", "high", "low", "open", "close", "volume")

    ##-------------------------------------------------------------------------
    def __init__(self, d, values):
        self.date = d
        self.high, self.low, self.open, self.close, self.volume = values

    ##-------------------------------------------------------------------------
    @property
    def value(self):
        return (self.high, self.low, self.open, self.close, self.volume)

    ##-------------------------------------------------------------------------
    def __str__(self):
        fmt = "{0!s}, {1:12.5f}, {2:12.5f}, {3:12.5f}, {4:12.5f}, {5:12.0f}"
        return fmt.format(self.date, self.high,
                          self.low, self.open, self.close, self.volume)

    ##-------------------------------------------------------------------------
    ##  support serialization

    def __getstate__(self):
        return (self.date, self.high, self.low,
                self.open, self.close, self.volume)

    def __setstate__(self, state):
        (self.date, self.high,
         self.low, self.open, self.close, self.volume) = state


###############################################################################
class HlocvCurve(GCurve):
    """
    Class representing a HLOCV curve, generally used for daily stock prices. It
    inherits from the generic GCurve.
    """
    __slots__ = ("data", "knot_cls")

    ##-------------------------------------------------------------------------
    def __init__(self, dates=None, values=None):
        super().__init__(dates, values, HlocvKnot)

    ##-------------------------------------------------------------------------
    ##  methods to return arrays for a specific HLOCV field:
    ##    - highs
    ##    - lows
    ##    - opens
    ##    - closes
    ##    - volumes

    @property
    def highs(self):
        return np.array([knot.high for knot in self.data])

    @property
    def lows(self):
        return np.array([knot.low for knot in self.data])

    @property
    def opens(self):
        return np.array([knot.open for knot in self.data])

    @property
    def closes(self):
        return np.array([knot.close for knot in self.data])

    @property
    def volumes(self):
        return np.array([knot.volume for knot in self.data])

    ##-------------------------------------------------------------------------
    ## some methods inherited from GCurve don't make sense for an HLOCV curve

    def __add__(self, other):
        raise NotImplementedError()

    def __radd__(self, scalar):
        raise NotImplementedError()

    def __rmul__(self, scalar):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    def curve(self, field="close"):
        """
        Description:
            Convert a HLOCV curve to a scalar curve.
        Inputs:
            field - choose among high, low, open, close, volume
        Returns:
            A new Curve.
        """
        return Curve(self.dates, [getattr(knt, field) for knt in self.data])

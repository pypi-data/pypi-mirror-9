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

from onyx.datatypes.date import Date
from onyx.datatypes.curve import Curve
from onyx.datatypes.gcurve import CurveError

import numpy as np
import unittest
import pickle


# --- Unit tests
class RegTest(unittest.TestCase):
    def setUp(self):
        # --- create a first curve by passing arrays of dates and values
        self.dates = [Date.parse(d)
                      for d in ["F08", "G08", "H08", "J08", "K08", "M08",
                                "N08", "Q08", "U08", "V08", "X08", "Z08"]]
        self.values = np.cumsum(np.ones(12))
        self.refcrv = Curve(self.dates, self.values)

    def tearDown(self):
        # --- perform clean-up actions, if any
        pass

    def test_len(self):
        self.assertEqual(len(self.refcrv.data), 12)

    def test_repr(self):
        self.assertEqual(self.refcrv, eval(repr(self.refcrv)))

    def test_get(self):
        d0 = Date(2007, 6, 1)
        d1 = Date(2008, 6, 1)
        d2 = Date(2008, 6, 15)
        d3 = Date(2008, 7, 15)
        d4 = Date(2009, 6, 1)
        self.assertEqual(self.refcrv[d0], 1.0)              # use interpolation
        self.assertEqual(self.refcrv[d1], 6.0)              # knot exists
        self.assertEqual(self.refcrv[d2], 6.0 + 14.0/30.0)  # use interpolation
        self.assertEqual(self.refcrv[d3], 7.0 + 14.0/31.0)  # use interpolation
        self.assertEqual(self.refcrv[d4], 12.0)             # use interpolation
        # --- get a know that doesn't exists
        self.assertRaises(IndexError, self.refcrv.get_knot, d0)
        # --- get an existing knot
        self.assertEqual(self.refcrv.get_knot(d1).value, 6.0)
        # --- get a know that doesn't exists
        self.assertRaises(IndexError, self.refcrv.get_knot, d2)
        # --- get a know that doesn't exists
        self.assertRaises(IndexError, self.refcrv.get_knot, d3)
        # --- get a know that doesn't exists
        self.assertRaises(IndexError, self.refcrv.get_knot, d4)

    def test_has(self):
        self.assertFalse(self.refcrv.has_knot(Date(2007, 6, 1)))
        self.assertTrue(self.refcrv.has_knot(Date(2008, 6, 1)))
        self.assertFalse(self.refcrv.has_knot(Date(2008, 6, 15)))
        self.assertFalse(self.refcrv.has_knot(Date(2009, 6, 1)))

    def test_constructurs(self):
        # --- create a second curve by adding knots iteratively
        crv = Curve()
        val = 0
        for d in self.dates:
            val += 1
            crv[d] = val
        # --- do the comparison of their string representation
        self.assertEqual(crv.__str__(), self.refcrv.__str__())
        # --- do the comparison of their internal representation
        self.assertEqual(crv.data, self.refcrv.data)
        # --- do comparison between curves
        self.assertEqual(crv, self.refcrv)
        # --- check constructor exceptions
        d = Date.today()
        self.assertRaises(CurveError, Curve, [d, d], [1, 1])
        self.assertRaises(CurveError, Curve,
                          ([Date(2008, 1, 1), Date(2008, 12, 1)], [1, 1, 1]))

    def test_back_and_front(self):
        self.assertEqual(self.refcrv.front,
                         self.refcrv.knot_cls(Date(2008, 1, 1), 1.0))
        self.assertEqual(self.refcrv.front.date, Date(2008, 1, 1))
        self.assertEqual(self.refcrv.front.value, 1.0)
        self.assertEqual(self.refcrv.back,
                         self.refcrv.knot_cls(Date(2008, 12, 1), 12.0))
        self.assertEqual(self.refcrv.back.date, Date(2008, 12, 1))
        self.assertEqual(self.refcrv.back.value, 12.0)

    def test_dates_and_values(self):
        values = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(sum(self.refcrv.values - values), 0.0)
        dates = np.array([733042, 733073, 733102, 733133, 733163, 733194,
                          733224, 733255, 733286, 733316, 733347, 733377])
        self.assertEqual(sum(self.refcrv.ordinals - dates), 0.0)

    def test_algebra(self):
        values = self.refcrv.values
        self.assertEqual(2.0*self.refcrv - self.refcrv*1.0, self.refcrv)
        self.assertEqual(2.0*self.refcrv / 2.0, self.refcrv)
        self.assertEqual(sum(1.0 / values), sum((1.0 / self.refcrv).values))
        self.assertEqual(sum(values*values),
                         sum((self.refcrv*self.refcrv).values))

    def test_pickling(self):
        crv = pickle.loads(pickle.dumps(self.refcrv, 2))
        # --- check that data representations are identical
        self.assertEqual(crv.data, self.refcrv.data)
        # --- check that string representations are identical
        self.assertEqual(crv.__str__(), self.refcrv.__str__())

    def test_crop(self):
        sd = Date.parse("N08")
        ed = Date.parse("X08")
        dates = [Date.parse(d) for d in ["N08", "Q08", "U08", "V08", "X08"]]
        values = [7, 8, 9, 10, 11]
        crv = Curve(dates, values)
        self.assertEqual(self.refcrv.crop(sd, ed), crv)

if __name__ == "__main__":
    unittest.main()

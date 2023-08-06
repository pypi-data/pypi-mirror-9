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
from onyx.datatypes.curve_functions import Interpolate, ApplyAdjustments

import numpy as np
import unittest


# --- unit tests
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

    def assertCurveEqual(self, crv1, crv2, precision):
        self.assertEqual(len(crv1), len(crv2))
        for i in range(len(crv1)):
            self.assertEqual(crv1.data[i].date, crv2.data[i].date)
            self.assertAlmostEqual(crv1.data[i].value,
                                   crv2.data[i].value, precision)

    def test_interpolate(self):
        dt = Date(2009, 1, 1)
        self.assertEqual(12, Interpolate(self.refcrv, dt))
        self.assertEqual(12, Interpolate(self.refcrv, dt, "Step"))
        self.assertEqual(12, Interpolate(self.refcrv, dt, "Linear"))

        dt = Date(2007, 1, 1)
        self.assertEqual(1, Interpolate(self.refcrv, dt))
        self.assertEqual(1, Interpolate(self.refcrv, dt, "Step"))
        self.assertEqual(1, Interpolate(self.refcrv, dt, "Linear"))

        dt = Date(2008, 11, 16)
        self.assertEqual(11, Interpolate(self.refcrv, dt))
        self.assertEqual(11, Interpolate(self.refcrv, dt, "Step"))
        self.assertEqual(11.5, Interpolate(self.refcrv, dt, "Linear"))

    def test_apply_adjustments(self):
        adj_crv = Curve([Date(2008, 6, 15)], [0.1])
        ref_crv = Curve(self.refcrv.dates,
                        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                         7.0, 8.0, 9.0, 10.0, 11.0, 12.0])

        self.assertCurveEqual(ApplyAdjustments(self.refcrv, adj_crv),
                              ref_crv, 8)

if __name__ == "__main__":
    unittest.main()

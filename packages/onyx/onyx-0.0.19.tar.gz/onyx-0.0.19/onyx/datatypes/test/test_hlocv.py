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

from onyx.datatypes.hlocv import HlocvCurve
from onyx.datatypes.date import Date

import numpy as np
import unittest
import pickle


# --- Unit tests
class RegTest(unittest.TestCase):
    def setUp(self):
        # --- generate random values
        x = np.cumsum(np.random.standard_normal(12+1))
        # --- create a test curve
        dates = [Date.parse(d)
                 for d in ["F08", "G08", "H08", "J08", "K08", "M08",
                           "N08", "Q08", "U08", "V08", "X08", "Z08"]]

        xh = lambda k: max(x[k], x[k+1])
        xl = lambda k: min(x[k], x[k+1])

        values = [(xh(k), xl(k), x[k], x[k+1], np.random.randint(0, 100))
                  for k in range(len(dates))]
        self.crv = HlocvCurve(dates, values)

    def tearDown(self):
        # --- perform clean-up actions, if any
        pass

    def testpickling(self):
        newcrv = pickle.loads(pickle.dumps(self.crv, 2))
        # --- check that internal data representations are identical
        self.assertEqual(newcrv.data, self.crv.data)
        # --- check that string representations are identical
        self.assertEqual(newcrv.__str__(), self.crv.__str__())

if __name__ == "__main__":
    unittest.main()

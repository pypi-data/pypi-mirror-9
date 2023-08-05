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

from onyx.datatypes.cache import DailyCache

import unittest


# --- Unit tests
class RegTest(unittest.TestCase):
    def setUp(self):
        # --- perform set-up actions, if any
        pass

    def tearDown(self):
        # --- perform clean-up actions, if any
        pass

    def test_daily(self):
        cache = DailyCache()
        cache["aaa"] = 123

        self.assertTrue("aaa"in cache)
        self.assertFalse("abc" in cache)
        self.assertEqual(cache["aaa"], 123)
        self.assertRaises(KeyError, cache.__getitem__, "abc")

if __name__ == "__main__":
    unittest.main()

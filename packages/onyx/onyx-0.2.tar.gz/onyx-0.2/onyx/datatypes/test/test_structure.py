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

from onyx.datatypes.structure import Structure

import unittest
import pickle


# --- Unit tests
class RegTest(unittest.TestCase):
    def setUp(self):
        # --- perform set-up actions, if any
        pass

    def tearDown(self):
        # --- perform clean-up actions, if any
        pass

    def test_constructors(self):
        # --- test different ways of creating the same structure
        # --- first: this doesn't preserve the order!!!
        struct1 = Structure({"a": 1, "b": 2, "c": 3})
        # --- second: this doesn't preserve the order!!!
        struct2 = Structure(a=1, b=2, c=3)
        # --- third: this preserves the order
        struct3 = Structure([("a", 1), ("b", 2), ("c", 3)])
        # --- fourth: this preserves the order
        struct4 = Structure()
        struct4["a"] = 1
        struct4["b"] = 2
        struct4["c"] = 3

        self.assertEqual(struct1, struct2)
        self.assertEqual(struct2, struct3)
        self.assertEqual(struct3, struct4)

    def test_algerba(self):
        struct1 = Structure([('a',  1), ('b',  2), ('c',  3)])
        struct2 = Structure([('b', 10), ('c', 10), ('d', 10)])

        add_struct = Structure([('a', 1), ('b', 12), ('c', 13), ('d', 10)])
        sub_struct = Structure([('a', -1), ('b', 8), ('c', 7), ('d', 10)])

        self.assertEqual(struct2 + struct1, add_struct)
        self.assertEqual(struct2 - struct1, sub_struct)

        iadd_struct = Structure([('a', 1), ('b', 12), ('c', 13), ('d', 10)])

        struct2 += struct1
        self.assertEqual(struct2, iadd_struct)

        rmul_struct = Structure([('a', -2), ('b', -4), ('c', -6)])

        self.assertEqual(-2*struct1, rmul_struct)

    def test_pickling(self):
        struct0 = Structure({"a": 1, "b": 2, "c": 3})
        struct1 = pickle.loads(pickle.dumps(struct0, 2))
        # --- check that data representations are identical
        self.assertEqual(struct0, struct1)
        # --- check that string representations are identical
        self.assertEqual(struct0.__str__(), struct1.__str__())

if __name__ == "__main__":
    unittest.main()

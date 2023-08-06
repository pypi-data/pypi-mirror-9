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


from onyx.database.objdb import ObjNotFound
from onyx.depgraph.graph import GraphNodeError
from onyx.depgraph.graph_api import (CreateInMemory,
                                     GetVal, SetVal, InvalidateNode, UseGraph)
from onyx.database.objdb_api import UseDatabase
from onyx.depgraph.test import ufo_testcls

import time
import unittest
import os


class timer(object):
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.elapsed = self.end - self.start
        return False


# --- Unit tests class
class TestGraph(unittest.TestCase):
    def setUp(self):
        self.use_db = UseDatabase(os.getenv("OBJDB_TEST", default="TestDb"))
        self.use_graph = UseGraph()
        self.use_db.__enter__()
        self.use_graph.__enter__()

        self.obj1 = CreateInMemory(ufo_testcls.TestCls1(Name="obj1"))
        self.obj2 = CreateInMemory(ufo_testcls.TestCls1(Name="obj2"))
        self.obj3 = CreateInMemory(ufo_testcls.TestCls2(Name="obj3",
                                                        Kid1=self.obj1.Name,
                                                        Kid2=self.obj2.Name))

    def tearDown(self):
        del self.obj1, self.obj2, self.obj3
        self.use_db.__exit__()
        self.use_graph.__exit__()

    def test_GetVal(self):
        # --- check that we retrive the correct values
        self.assertEqual(GetVal("obj1", "attr1"), 333.0)
        self.assertEqual(GetVal("obj1", "attr2"), 666.0)
        self.assertEqual(GetVal("obj1", "A"), 1003.0)
        self.assertEqual(GetVal(self.obj1, "A"), 1003.0)
        self.assertEqual(GetVal("obj1", "C", 0, 0), 666.0)
        self.assertEqual(GetVal("obj1", "C", 1, 0), 667.0)
        self.assertEqual(GetVal("obj1", "C", x=1), 667.0)
        self.assertEqual(GetVal("obj1", "C", 0, 2), 668.0)
        self.assertEqual(GetVal("obj1", "C", 0, y=2), 668.0)
        self.assertEqual(GetVal("obj3", "A"), 2006.0)
        self.assertEqual(GetVal("obj1", "A"), GetVal("obj1", "A"))

    def test_caching(self):
        # --- compute A the first time
        with timer() as t:
            val = GetVal("obj1", "A")
        self.assertEqual(val, 1003.0)
        self.assertAlmostEqual(t.elapsed, 4.0, 1)

        # --- compute A a second time: result is cached
        with timer() as t:
            val = GetVal("obj1", "A")
        self.assertEqual(val, 1003.0)
        self.assertAlmostEqual(t.elapsed, 0.0, 1)

        # --- invalidate C and recalculate A: should only have to recalculate
        #     one of the two children
        InvalidateNode(self.obj1, "C")
        with timer() as t:
            val = GetVal("obj1", "A")
        self.assertEqual(val, 1003.0)
        self.assertAlmostEqual(t.elapsed, 2.0, 1)

        # --- try once more: should be cached again
        with timer() as t:
            val = GetVal("obj1", "A")
        self.assertEqual(val, 1003.0)
        self.assertAlmostEqual(t.elapsed, 0.0, 1)

    def test_exceptions(self):
        self.assertRaises(ObjNotFound, GetVal, "xxx", "xxx")
        self.assertRaises(AttributeError, GetVal, "obj1", "xxx")
        self.assertRaises(GraphNodeError, SetVal, "obj1", "A", "Hello World")
        self.assertRaises(GraphNodeError, SetVal, "obj1", "B", 0)

if __name__ == "__main__":
    unittest.main()

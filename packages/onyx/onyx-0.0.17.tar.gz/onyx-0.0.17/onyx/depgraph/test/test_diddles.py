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

from onyx.depgraph.graph_api import CreateInMemory, GetVal
from onyx.depgraph.diddles import EvalBlock, DiddleScope, SetDiddle

from onyx.database.objdb_api import UseDatabase
from onyx.depgraph.graph_api import UseGraph
from onyx.depgraph.test import ufo_testcls

import unittest
import os


class RegTest(unittest.TestCase):
    def setUp(self):
        self.use_db = UseDatabase(os.getenv("OBJDB_TEST", default="TestDb"))
        self.use_graph = UseGraph()
        self.use_db.__enter__()
        self.use_graph.__enter__()

        self.obj = CreateInMemory(ufo_testcls.TestCls3(Name="obj"))

    def tearDown(self):
        del self.obj
        self.use_db.__exit__()
        self.use_graph.__exit__()

    def node_assertEqual(self, obj, vt, value):
        self.assertEqual(GetVal(self.obj.Name, vt), value)
        self.assertEqual(GetVal(self.obj, vt), value)

    def test_evalblock(self):
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- create an eval block
        with EvalBlock() as ev_block:
            self.node_assertEqual(self.obj, "Number", 666.0)
            self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

            # --- now diddle Number to 0
            SetDiddle("obj", "Number", 0, ev_block)
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            # --- test nested eval blocks
            with EvalBlock() as new_ev_block:
                # --- diddle Number to 333 passing new diddle scope
                SetDiddle("obj", "Number", 333, new_ev_block)
                self.node_assertEqual(self.obj, "CalcProperty", 667.0)

            # --- outside nested eval block
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            # --- now diddle the calc VT itself
            SetDiddle("obj", "CalcProperty", 1976, ev_block)
            self.node_assertEqual(self.obj, "CalcProperty", 1976)

            with EvalBlock() as new_ev_block:
                SetDiddle("obj", "CalcProperty", 333, new_ev_block)
                self.node_assertEqual(self.obj, "CalcProperty", 333)

            # --- outside nested diddle eval block
            self.node_assertEqual(self.obj, "CalcProperty", 1976)

        # --- outside all eval blocks
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

    def test_diddlescope_basicusage(self):
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- create a diddle scope and set a first diddle
        scope = DiddleScope()
        scope.set_diddle(self.obj, "Number", 0.0)

        # --- the diddle is set, but not yet used
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- use the diddle scope to enforce existing diddles and to add more
        with scope:
            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", 1.0)

            scope.set_diddle(self.obj, "CalcProperty", "ABC")

            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", "ABC")

        # --- outside diddle scope
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

        # --- a diddle scope can be reused and all diddles are re-enforced
        # --- use the diddle scope to enforce existing diddles and to add more
        with scope:
            self.node_assertEqual(self.obj, "Number", 0.0)
            self.node_assertEqual(self.obj, "CalcProperty", "ABC")

        # --- outside diddle scope
        self.node_assertEqual(self.obj, "Number", 666.0)
        self.node_assertEqual(self.obj, "CalcProperty", 1333.0)

if __name__ == "__main__":
    unittest.main()

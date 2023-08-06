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
from onyx.database.objdb import ObjDbDummyClient, ObjNotFound
from onyx.database.objdb_api import (UseDatabase, ExistsInDatabase, ObjDbQuery,
                                     AddObj, GetObj, UpdateObj, DelObj)

from onyx.database.test import ufo_testcls

import unittest
import os


# --- test API with a dummy client
class Test_Dummy(unittest.TestCase):
    def setUp(self):
        self.obj = ufo_testcls.ufocls(Name="test")
        self.clt = ObjDbDummyClient("dummy_db", "dummy_user")

    def test_add_get_update_delete(self):
        with UseDatabase(self.clt):
            self.assertRaises(ObjNotFound, GetObj, self.obj.Name, False)
            self.assertEqual(AddObj(self.obj), self.obj)
            self.assertEqual(GetObj(self.obj.Name), self.obj)

            self.obj.Birthday = Date.now()
            self.assertEqual(UpdateObj(self.obj), self.obj)

            DelObj(self.obj)
            self.assertRaises(ObjNotFound, GetObj, self.obj.Name)

    def test_exists(self):
        with UseDatabase(self.clt):
            self.assertFalse(ExistsInDatabase(self.obj.Name))
            AddObj(self.obj)
            self.assertTrue(ExistsInDatabase(self.obj.Name))
            DelObj(self.obj)
            self.assertFalse(ExistsInDatabase(self.obj.Name))


# --- test API with the postgres client on TestDb
class Test_Postgres(unittest.TestCase):
    def setUp(self):
        self.obj = ufo_testcls.ufocls(Name="test")
        self.clt = os.getenv("OBJDB_TEST", default="TestDb")

    def test_add_get_update_delete(self):
        with UseDatabase(self.clt):
            try:
                self.assertRaises(ObjNotFound, GetObj, self.obj.Name, False)
                self.assertEqual(AddObj(self.obj), self.obj)

                self.assertEqual(GetObj(self.obj.Name, True), self.obj)
                self.assertEqual(GetObj(self.obj.Name, True).Birthday,
                                 self.obj.Birthday)
                self.assertEqual(GetObj(self.obj.Name, True).OtherDates,
                                 self.obj.OtherDates)
                self.assertEqual(GetObj(self.obj.Name, True).SimpleCurve,
                                 self.obj.SimpleCurve)

                self.obj.Birthday = Date.now()
                self.assertEqual(UpdateObj(self.obj), self.obj)

                self.assertEqual(GetObj(self.obj.Name, True), self.obj)

                DelObj(self.obj)
                self.assertRaises(ObjNotFound, GetObj, self.obj.Name)

            finally:
                # --- try cleaning up irrespective of failures
                ObjDbQuery("DELETE FROM Objects "
                           "WHERE Name=%s", (self.obj.Name,))
                ObjDbQuery("DELETE FROM ClassDefinitions "
                           "WHERE ObjType=%s", (self.obj.ObjType,))

    def test_exists(self):
        with UseDatabase(self.clt):
            try:
                self.assertFalse(ExistsInDatabase(self.obj.Name))
                AddObj(self.obj)
                self.assertTrue(ExistsInDatabase(self.obj.Name))
                DelObj(self.obj)
                self.assertFalse(ExistsInDatabase(self.obj.Name))

            finally:
                # --- try cleaning up irrespective of failures
                ObjDbQuery("DELETE FROM Objects "
                           "WHERE Name=%s", (self.obj.Name,))
                ObjDbQuery("DELETE FROM ClassDefinitions "
                           "WHERE ObjType=%s", (self.obj.ObjType,))

if __name__ == "__main__":
    unittest.main()

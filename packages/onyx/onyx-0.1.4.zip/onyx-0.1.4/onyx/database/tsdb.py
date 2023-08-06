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

from onyx.datatypes.curve import Curve, Knot
from onyx.datatypes.hlocv import HlocvCurve, HlocvKnot
from onyx.datatypes.date import Date
from onyx.database.objdb import typecast_to_Date

import psycopg2 as psql
import psycopg2.extras as psql_extras
import psycopg2.extensions as psql_ext
import sys

__all__ = ["TsNotFound", "TsDbError", "TsDbClient"]

# --- column names for HLOCVCurves
HLOCV_FIELDS = ("High", "Low", "Open", "Close", "Volume")

# --- define standard query strings
QUERY_TS_EXISTS = """
SELECT EXISTS (SELECT 1 FROM {0:s} WHERE Name=%s) AS "exists";"""


###############################################################################
class TsNotFound(Exception):
    pass


###############################################################################
class TsDbError(Exception):
    pass


##-----------------------------------------------------------------------------
def print_error(cursor):
    print("QUERY:\n{0:s}".format(cursor.query), file=sys.stderr)


###############################################################################
class TsDbClient(object):
    """
    Description:
        TsDb database, client class. It exposes a minimal api.
    """
    core_tables = ("Curves", "HLOCVCurves")

    ##-------------------------------------------------------------------------
    def __init__(self, database, user, host=None, check=True):
        self.dbname = database
        self.user = user
        self.host = host

        self.conn = psql.connect(host=host, database=database, user=user,
                                 cursor_factory=psql_extras.NamedTupleCursor)
        self.conn.set_isolation_level(psql_ext.ISOLATION_LEVEL_AUTOCOMMIT)

        # --- register typecast to Date for date, timpestamp, timestamptz
        curs = self.conn.cursor()
        curs.execute("SELECT NULL::date, NULL::timestamp, NULL::timestamptz;")
        oids = tuple([col.type_code for col in curs.description])
        psql_ext.register_type(psql_ext.new_type(oids, "Date",
                                                 typecast_to_Date))

        # --- validation: without the following tables in the backend the
        #                 client doesn't work properly.
        if check:
            curs = self.conn.cursor()
            for table in self.core_tables:
                try:
                    curs.execute("SELECT 1 FROM {0:s} LIMIT 1;".format(table))
                except psql.ProgrammingError:
                    raise RuntimeError("Table {0:s} is missing for "
                                       "{1:s}".format(table, self.dbname))

    ##-------------------------------------------------------------------------
    def initialize(self):
        curs = self.conn.cursor()
        curs.execute("""
            -- Curves table
            CREATE TABLE
            Curves (
                Date  timestamptz      NOT NULL,
                Name  varchar(64)      NOT NULL,
                Value double precision NOT NULL,
                CONSTRAINT CrvDateName UNIQUE (Date, Name) );

            CREATE INDEX crv_by_name_idx ON Curves (Name);

            -- HlocvCurves table
            CREATE TABLE
            HlocvCurves (
                Date   timestamptz      NOT NULL,
                Name   varchar(64)      NOT NULL,
                High   double precision NOT NULL,
                Low    double precision NOT NULL,
                Open   double precision NOT NULL,
                Close  double precision NOT NULL,
                Volume double precision NOT NULL,
                CONSTRAINT HlocvDateName UNIQUE (Date, Name) );

            CREATE INDEX hlocv_by_name_idx ON HlocvCurves (Name);""")

    ##-------------------------------------------------------------------------
    def restart(self):
        self.close()
        self.conn = psql.connect(host=self.host,
                                 database=self.dbname, user=self.user)
        self.conn.set_isolation_level(psql_ext.ISOLATION_LEVEL_AUTOCOMMIT)

    ##-------------------------------------------------------------------------
    def close(self):
        if hasattr(self, "conn") and not self.conn.closed:
            self.conn.close()

    ##-------------------------------------------------------------------------
    def get_row_by(self, table, name, date=None, strict=False):
        if date is None:
            query = """SELECT * FROM {0:s} WHERE Name=%s AND Date IN
                       (SELECT MAX(Date) FROM {0:s} WHERE Name=%s);"""
            parms = (name, name)
        elif strict:
            query = "SELECT * FROM {0:s} WHERE Name=%s AND Date=%s;"
            parms = (name, date)
        else:
            query = """SELECT * FROM {0:s} WHERE Name=%s AND Date IN
                       (SELECT MAX(Date)
                        FROM {0:s} WHERE Name=%s AND Date<=%s);"""
            parms = (name, name, date)

        curs = self.conn.cursor()
        try:
            curs.execute(query.format(table), parms)
        except psql.OperationalError:
            print_error(curs)
            raise

        row = curs.fetchone()
        curs.close()

        if row is None:
            if strict and date is not None:
                raise TsNotFound("Row not found for curve {0:s} in {1:s}"
                                 "and date {2:s}".format(name, table, date))
            else:
                raise TsNotFound("No rows were found "
                                 "for {0:s} in {1:s}".format(name, table))
        else:
            return row

    ##-------------------------------------------------------------------------
    def get_curve(self, name, start=None, end=None):
        if start is None:
            if end is None:
                # --- neither start nor end are specified
                parms = name,
                query = "SELECT Date, Value FROM Curves WHERE Name=%s;"
                errmsg = "No data found in Curves for {0:s}".format(name)
            else:
                # --- end is specified, start is not
                parms = name, end
                query = """SELECT Date, Value FROM Curves
                           WHERE Name = %s AND Date <= %s;"""
                errmsg = "No data found in " \
                         "Curves for {0:s}, end = {1:s}".format(name, end)
        elif end is None:
            # --- start is specified, end is not
            parms = name, start
            query = """SELECT Date, Value FROM Curves
                       WHERE Name = %s AND Date >= %s;"""
            errmsg = "No data found in Curves " \
                     "for {0:s}, start = {1:s}".format(name, start)
        else:
            # --- both start and end are specified
            parms = name, start, end
            query = """SELECT Date, Value
                       FROM Curves
                       WHERE Name = %s AND Date BETWEEN %s AND %s;"""
            errmsg = "No data found in Curves for {0:s}, " \
                     "start = {1:s} end = {2:s}".format(name, start, end)

        # --- create a cursor, check if ts exists and execute query
        curs = self.conn.cursor()
        try:
            curs.execute(QUERY_TS_EXISTS.format("Curves"), (name, ))
        except psql.OperationalError:
            print_error(curs)
            raise

        if not curs.fetchone().exists:
            raise TsNotFound("Time Series {0:s} not "
                             "found in Curves table".format(name))

        try:
            curs.execute(query, parms)
        except psql.OperationalError:
            print_error(curs)
            raise
        else:
            # --- populate a curve with the query's results
            crv = Curve.__new__(Curve)
            crv.knot_cls = Knot
            crv.data = [Knot(Date.parse(r[0]), r[1]) for r in curs.fetchall()]
            crv.data.sort()
        finally:
            curs.close()

        # --- raise exception if curve is empty
        if not len(crv):
            raise TsNotFound(errmsg)

        return crv

    ##-------------------------------------------------------------------------
    def get_hlocv(self, name, start=None, end=None, field=None):
        if start is None:
            if end is None:
                # --- neither start nor end are specified
                parms = name,
                query = """SELECT
                           Date, High, Low, Open, Close, Volume
                           FROM HLOCVCurves
                           WHERE Name = %s;"""
                errmsg = "No data found in HLOCVCurves for {0:s}".format(name)
            else:
                # --- end is specified, start is not
                parms = name, end
                query = """SELECT
                           Date, High, Low, Open, Close, Volume
                           FROM HLOCVCurves
                           WHERE Name = %s AND Date <= %s;"""
                errmsg = "No data found in " \
                         "HLOCVCurves for {0:s}, end = {1:s}".format(name, end)
        elif end is None:
            # --- start is specified, end is not
            parms = name, start
            query = """SELECT
                       Date, High, Low, Open, Close, Volume
                       FROM HLOCVCurves
                       WHERE Name = %s AND Date >= %s;"""
            errmsg = "No data found in " \
                     "HLOCVCurves for {0:s}, start = {1:s}".format(name, start)
        else:
            # --- both start and end are specified
            parms = name, start, end
            query = """SELECT
                       Date, High, Low, Open, Close, Volume
                       FROM HLOCVCurves
                       WHERE Name = %s AND Date BETWEEN %s AND %s;"""
            errmsg = "No data found in HLOCVCurves for {0:s}, " \
                     "start = {1:s} end = {2:s}".format(name, start, end)

        # --- create a cursor, check if ts exists and execute query
        curs = self.conn.cursor()
        try:
            curs.execute(QUERY_TS_EXISTS.format("HLOCVCurves"), (name, ))
        except psql.OperationalError:
            print_error(curs)
            raise
        if not curs.fetchone().exists:
            raise TsNotFound("Time Series {0:s} not found "
                             "in HLOCVCurves table".format(name))

        try:
            curs.execute(query, parms)
        except psql.OperationalError:
            print_error(curs)
            raise
        else:
            rows = curs.fetchall()
            if field is None:
                crv = HlocvCurve.__new__(HlocvCurve)
                crv.knot_cls = HlocvKnot
                crv.data = [HlocvKnot(Date.parse(r[0]), r[1:]) for r in rows]
            else:
                idx = 1 + HLOCV_FIELDS.index(field)
                crv = Curve.__new__(Curve)
                crv.knot_cls = Knot
                crv.data = [Knot(Date.parse(r[0]), r[idx]) for r in rows]
            crv.data.sort()
        finally:
            curs.close()

        # --- raise exception if curve is empty
        if not len(crv):
            raise TsNotFound(errmsg)

        return crv

    ##-------------------------------------------------------------------------
    def upsert_curve(self, name, crv, crv_type="CRV"):
        if crv_type == "HLOCV":
            upd_unpack = lambda k: (k.high, k.low, k.open,
                                    k.close, k.volume, k.date, name)
            ins_unpack = lambda k: (k.date, name, k.high,
                                    k.low, k.open, k.close, k.volume)
        else:
            upd_unpack = lambda k: (k.value, k.date, name)
            ins_unpack = lambda k: (k.date, name, k.value)

        ins = []
        upd = []

        try:
            # --- get existing curve
            if crv_type == "HLOCV":
                curr_crv = self.get_hlocv(name, crv.front.date, crv.back.date)
            else:
                curr_crv = self.get_curve(name, crv.front.date, crv.back.date)
        except TsNotFound:
            ins = [ins_unpack(knot) for knot in crv]
        else:
            # --- loop over all knots and check which one needs updating
            #     and which one needs inserting
            for knot in crv:
                try:
                    curr_knot = curr_crv.get_knot(knot.date)
                    # --- knot exists already, update if value has changed
                    if curr_knot.value != knot.value:
                        upd.append(upd_unpack(knot))
                except IndexError:
                    # --- knot not found, insert
                    ins.append(ins_unpack(knot))

        if crv_type == "HLOCV":
            ins_query = "INSERT INTO HlocvCurves VALUES (%s,%s,%s,%s,%s,%s,%s)"
            upd_query = """UPDATE HlocvCurves
                           SET
                           High = %s,
                           Low = %s,
                           Open = %s,
                           Close = %s,
                           Volume = %s
                           WHERE Date = %s AND Name = %s"""
        else:
            ins_query = "INSERT INTO Curves VALUES (%s,%s,%s)"
            upd_query = """UPDATE Curves
                           SET
                           Value = %s
                           WHERE Date = %s AND Name = %s"""

        curs = self.conn.cursor()

        if len(ins):
            curs.executemany(ins_query, ins)
        if len(upd):
            curs.executemany(upd_query, upd)

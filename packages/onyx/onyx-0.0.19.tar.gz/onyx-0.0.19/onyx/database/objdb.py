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
from onyx.database.ufo_base import SPECIAL

import psycopg2 as psql
import psycopg2.extras as psql_extras
import psycopg2.extensions as psql_ext
import psycopg2.errorcodes as psql_err
import pylru
import weakref
import pickle
import getpass
import abc

__all__ = ["ObjNotFound", "ObjDbError", "ObjExists", "ObjDbClient"]

USER = getpass.getuser()

# --- define standard query strings and error messages

QUERY_CLS_INSERT = "INSERT INTO ClassDefinitions VALUES (%s,%s);"
QUERY_CLS_GET = """
SELECT ClassDef FROM ClassDefinitions WHERE ObjType=%s;"""
QUERY_CLS_DELETE = """
DELETE FROM ClassDefinitions row WHERE row.ObjType=%s AND NOT
EXISTS (SELECT 1 FROM Objects WHERE ObjType=row.ObjType);"""

QUERY_OBJ_INSERT = "INSERT INTO Objects VALUES (%s,%s,%s,%s,%s,%s,%s);"
QUERY_OBJ_GET = """
SELECT Name, ObjType, Version, ChangedBy, TimeCreated, LastUpdated, Data
FROM Objects WHERE Name=%s;"""
QUERY_OBJ_UPDATE = """
UPDATE Objects
SET Version=%s, ChangedBy=%s, LastUpdated=%s, Data=%s
WHERE Name=%s AND Version=%s;"""
QUERY_OBJ_DELETE = """
WITH deleted_row AS (
    DELETE FROM Objects
    WHERE  Name=%s AND Version=%s
    RETURNING ObjType, Name)
DELETE FROM ClassDefinitions cls_def
USING deleted_row
WHERE cls_def.ObjType = deleted_row.ObjType
AND NOT EXISTS (
   SELECT 1 FROM Objects objs
   WHERE objs.ObjType = deleted_row.ObjType
   AND objs.Name <> deleted_row.Name );"""
QUERY_OBJ_VERSION = "SELECT Version FROM Objects WHERE Name=%s LIMIT 1;"
QUERY_OBJ_EXISTS = """
SELECT EXISTS (SELECT 1 FROM Objects WHERE Name=%s) AS "exists";"""

QUERY_ARC_INSERT = "INSERT INTO Archive VALUES (%s,%s,%s,%s,%s,%s);"

MSG_RELOAD = """
Instance of {0:s} is older (v.{1:d}) than the most recent version in database
(v.{2:d}): reload object from database before updating"""


###############################################################################
class ObjNotFound(Exception):
    pass


###############################################################################
class ObjDbError(Exception):
    pass


###############################################################################
class ObjExists(ObjDbError):
    pass


###############################################################################
class dummy_conn(object):
    """
    This is a dummy connection class that implements placeholders methods
    used to support transactions. It is used by the base and dummy clients
    and should not be used by production implementations.
    """
    def set_isolation_level(self, *args):
        pass

    def tpc_begin(self, *args):
        pass

    def tpc_commit(self, *args):
        pass

    def tpc_rollback(self, *args):
        pass


###############################################################################
class ObjDbBase(object):
    """
    Base class for ObjDb clients.
    """
    ##-------------------------------------------------------------------------
    def __init__(self, database, user, host=None):
        self.dbname = database
        self.user = user
        self.host = host

        # --- weak references to all queried objects are kept here. Subsequent
        #     queries for the same object will return a reference if the object
        #     is still alive (i.e. they have not been disposed of by the gc).
        #     weak references will be kept alive by:
        #       - the cache of the db-client
        #       - the cache of the dependency graph
        self.refs = weakref.WeakValueDictionary()

        # --- unlimited caching
        self.cache = {}

        # --- lookup dictionary for class definitions
        self.class_defs = {}

        # --- the connection to the db-backend
        self.conn = dummy_conn()

        # --- store current transaction name
        self.transaction = None

    ##-------------------------------------------------------------------------
    def class_lookup(self, cls_name):
        """
        Lookup class by class name.
        """
        return self.class_defs[cls_name]

    ##-------------------------------------------------------------------------
    ##  implements methods to retrieve, add and remove items from db-cache

    def __getitem__(self, name):
        return self.refs[name]

    def __setitem__(self, name, instance):
        self.cache[name] = instance
        self.refs[name] = instance

    def __delitem__(self, name):
        try:
            del self.cache[name]
            del self.refs[name]
        except KeyError:
            pass

    ##-------------------------------------------------------------------------
    ##  method to test if an object exists in database. the base class
    ##  implementation only checks if a reference exsists without testing the
    ##  backend.
    def __contains__(self, name):
        return name in self.refs

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def initialize(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def restart(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def close(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def add(self, obj):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def get(self, name, refresh=False):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def update(self, obj):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def delete(self, obj):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def add_dated(self, obj, date):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def get_dated(self, name, date, strict=False):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def update_dated(self, obj, date, override=False):
        raise NotImplementedError()


##-----------------------------------------------------------------------------
def typecast_to_Date(value, curs):
    if value is None:
        return None
    else:
        # --- maybe we should use a regexp like r"^.*'(.*)'.*$" ???
        return Date.parse(value)


###############################################################################
class ObjDbClient(ObjDbBase):
    core_tables = ("ClassDefinitions", "Objects", "Archive")

    ##-------------------------------------------------------------------------
    def __init__(self, database, user, host=None, cache_size=500, check=True):
        """
        Description:
            ObjDb database, client class. It exposes a minimal api.
        """
        super().__init__(database, user, host)

        # --- The database cache is used to keep a limited number of previously
        #     retrieved objects "alive" (see above).
        self.cache = pylru.lrucache(cache_size)

        # --- open database connection
        self.conn = psql.connect(host=host, database=database, user=user,
                                 cursor_factory=psql_extras.NamedTupleCursor)
        self.conn.set_isolation_level(psql_ext.ISOLATION_LEVEL_AUTOCOMMIT)

        # --- register typecast to Date for date, timpestamp, timestamptz
        curs = self.conn.cursor()
        curs.execute("SELECT NULL::date, NULL::timestamp, NULL::timestamptz;")
        oids = tuple([col.type_code for col in curs.description])
        psql_ext.register_type(psql_ext.new_type(oids, "Date",
                                                 typecast_to_Date))

        # --- register a no-op loads() function to turn-off automatic parsing
        #     of json/jsonb datatype
        psql_extras.register_default_json(loads=lambda x: x)
        psql_extras.register_default_jsonb(loads=lambda x: x)

        # --- validation: without the following tables in the backend the
        #                 client doesn't work properly.
        if check:
            curs = self.conn.cursor()
            for table in self.core_tables:
                try:
                    curs.execute("SELECT 1 FROM {0:s} LIMIT 1;".format(table))
                except psql.ProgrammingError:
                    raise RuntimeError("Table {0!s} is missing on "
                                       "{1!s}".format(table, self.dbname))

    ##-------------------------------------------------------------------------
    def initialize(self):
        curs = self.conn.cursor()
        curs.execute("""
            -- this table is used to lookup class definition from class name
            CREATE TABLE
            ClassDefinitions (
                ObjType  varchar(64) PRIMARY KEY,
                ClassDef bytea       NOT NULL );

            -- this table is used to store UFO objects
            CREATE TABLE
            Objects (
                Name        varchar(64) PRIMARY KEY,
                ObjType     varchar(64) REFERENCES ClassDefinitions,
                Version     integer     NOT NULL,
                ChangedBy   varchar(64) NOT NULL,
                TimeCreated timestamptz NOT NULL,
                LastUpdated timestamptz NOT NULL,
                Data        jsonb       NOT NULL );

            CREATE INDEX objects_objtype_idx ON Objects (ObjType);

            -- this table is used to store archived (i.e. dated) objects
            CREATE TABLE
            Archive (
                Name      varchar(64) REFERENCES Objects,
                ObjType   varchar(64) REFERENCES ClassDefinitions,
                Date      date        NOT NULL,
                ChangedBy varchar(64) NOT NULL,
                TimeStamp timestamptz NOT NULL,
                Data      jsonb       NOT NULL,
                CONSTRAINT NameDate UNIQUE (Name, Date) );

            CREATE INDEX archive_name_idx ON Archive (Name);""")

    ##-------------------------------------------------------------------------
    def class_lookup(self, cls_name):
        try:
            return self.class_defs[cls_name]
        except KeyError:
            curs = self.conn.cursor()
            curs.execute(QUERY_CLS_GET, (cls_name,))
            row = curs.fetchone()
            if row is None:
                raise KeyError("Class definition unavailable for"
                               "{0!s} in {1!s}".format(cls_name, self.dbname))
            else:
                cls = pickle.loads(bytes(row[0]))
                self.class_defs[cls_name] = cls
                return cls

    ##-------------------------------------------------------------------------
    def __contains__(self, name):
        if name in self.refs:
            return True
        curs = self.conn.cursor()
        curs.execute(QUERY_OBJ_EXISTS, (name,))
        return curs.fetchone().exists

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
    def add(self, obj):
        curs = self.conn.cursor()

        # --- validate object's Name
        if not isinstance(obj.Name, str):
            if obj.Name is None:
                raise ObjDbError("Cannot persist objects with undefined Name")
            else:
                raise ObjDbError("Name attribute must be "
                                 "a string: {0!s}".format(type(obj.Name)))

        # --- if class definition is missing, add it to ClassDefinitions table
        try:
            cls = self.class_lookup(obj.ObjType)
        except KeyError:
            cls = psql.Binary(pickle.dumps(obj.__class__,
                                           protocol=pickle.HIGHEST_PROTOCOL))
            curs.execute(QUERY_CLS_INSERT, (obj.ObjType, cls))

        # --- serialize object and create record
        record = (obj.Name, obj.ObjType, obj.Version, obj.ChangedBy,
                  obj.TimeCreated, obj.LastUpdated, obj.to_json())

        # --- DB Insert
        try:
            curs.execute(QUERY_OBJ_INSERT, record)
        except psql.IntegrityError as err:
            if psql_err.lookup(err.pgcode) == "UNIQUE_VIOLATION":
                raise ObjExists("Object {0!s} already in "
                                "{1!s}".format(obj.Name, self.dbname))
            else:
                raise ObjDbError("{0!s}. Name = "
                                 "{1!s}".format(err.message, obj.Name))
        finally:
            curs.close()

        self[obj.Name] = obj
        return obj

    ##-------------------------------------------------------------------------
    def get(self, name, refresh=False):
        try:
            # --- if object must be retrieved from database raise exception and
            #     fall back
            if refresh:
                raise KeyError()
            # --- then try getting obj from database cache
            return self[name]
        except KeyError:
            # --- if not found in the db cache, get it from the database
            curs = self.conn.cursor()
            curs.execute(QUERY_OBJ_GET, (name,))
            row = curs.fetchone()
            curs.close()

            if row is None:
                raise ObjNotFound("Object '{0!s}' not found "
                                  "in {1!s}".format(name, self.dbname))
            else:
                cls = self.class_lookup(row.objtype)
                obj = cls.__new__(cls)

                for attr in SPECIAL:
                    setattr(obj, attr, getattr(row, attr.lower()))

                obj.from_json(row.data)

            self[obj.Name] = obj
            return obj

    ##-------------------------------------------------------------------------
    def update(self, obj):
        curs = self.conn.cursor()

        # --- current version is used by the update query
        curr_ver = obj.Version

        # --- update time-stamp and version on the object
        obj.LastUpdated = Date.now()
        obj.ChangedBy = USER.upper()
        obj.Version += 1

        # --- serialize data and create record
        record = (obj.Version, obj.ChangedBy,
                  obj.LastUpdated, obj.to_json(), obj.Name, curr_ver)

        try:
            curs.execute(QUERY_OBJ_UPDATE, record)

            if curs.rowcount == 0:
                # --- upadte failed: check why
                curs.execute(QUERY_OBJ_VERSION, (obj.Name,))
                res = curs.fetchone()

                if res is None:
                    raise ObjNotFound("Object '{0!s}' not found "
                                      "in {1!s}".format(obj.Name, self.dbname))

                if curr_ver < res.version:
                    msg = MSG_RELOAD.format(obj.Name, curr_ver, res.version)
                    raise ObjDbError(msg)

            else:
                self[obj.Name] = obj
                return obj

        except psql.IntegrityError as err:
            raise ObjDbError("{0!s}. Name = "
                             "{1!s}".format(err.message, obj.Name))
        finally:
            curs.close()

    ##-------------------------------------------------------------------------
    def delete(self, obj):
        # --- call the delete method if available
        if hasattr(obj, "delete"):
            obj.delete()

        try:
            # --- DB Delete
            curs = self.conn.cursor()
            curs.execute(QUERY_OBJ_DELETE, (obj.Name, obj.Version))

            if curs.rowcount == 0:
                # --- delete failed: check why
                curs.execute(QUERY_OBJ_VERSION, (obj.Name,))
                res = curs.fetchone()

                if res is None:
                    raise ObjNotFound("Object '{0!s}' not found "
                                      "in {1!s}".format(obj.Name, self.dbname))
                elif obj.Version < res.version:
                    msg = MSG_RELOAD.format(obj.Name, obj.Version, res.version)
                    raise ObjDbError(msg)
                else:
                    raise ObjDbError("Deletion of {0!s} failed without "
                                     "an obvious cause...".format(obj.Name))
        finally:
            curs.close()
            del self[obj.Name]

    ##-------------------------------------------------------------------------
    def add_dated(self, obj, date):
        curs = self.conn.cursor()

        # --- validate object's Name
        if not isinstance(obj.Name, str):
            if obj.Name is None:
                raise ObjDbError("Cannot persist objects with undefined Name")
            else:
                raise ObjDbError("Name attribute must be "
                                 "a string: {0!s}".format(type(obj.Name)))

        # --- if class definition is missing, add it to ClassDefinitions table
        try:
            cls = self.class_lookup(obj.ObjType)
        except KeyError:
            cls = psql.Binary(pickle.dumps(obj.__class__,
                                           protocol=pickle.HIGHEST_PROTOCOL))
            curs.execute(QUERY_CLS_INSERT, (obj.ObjType, cls))

        # --- serialize object and create record
        record = (obj.Name, obj.ObjType, date,
                  obj.ChangedBy, obj.LastUpdated, obj.to_json())

        # --- DB Insert
        try:
            curs.execute(QUERY_ARC_INSERT, record)
        except psql.IntegrityError as err:
            if psql_err.lookup(err.pgcode) == "UNIQUE_VIOLATION":
                raise ObjExists("Object {0!s} already in "
                                "{1!s}".format(obj.Name, self.dbname))
            else:
                raise ObjDbError("{0!s}. Name = "
                                 "{1!s}".format(err.message, obj.Name))
        finally:
            curs.close()

        self[(obj.Name, date)] = obj
        return obj

    ##-------------------------------------------------------------------------
    def get_dated(self, name, date, strict=False):
        try:
            # --- then try getting obj from database cache
            return self[(name, date)]
        except KeyError:
            if strict:
                query = """SELECT
                           ObjType, Date, ChangedBy, TimeStamp, Data
                           FROM Archive
                           WHERE Name = %s AND Date = %s;"""
                parms = (name, date)
            else:
                query = """SELECT
                           ObjType, Date, ChangedBy, TimeStamp, Data
                           FROM Archive
                           WHERE Name = %s AND Date IN
                               (SELECT MAX(Date) FROM Archive
                                WHERE Name = %s AND Date <= %s);"""
                parms = (name, name, date)

            curs = self.conn.cursor()
            curs.execute(query, parms)
            row = curs.fetchone()
            curs.close()

            if row is None:
                raise ObjNotFound("Archived object '{0!s}' not "
                                  "found for date {1!s}".format(name, date))
            else:
                cls = self.class_lookup(row.objtype)
                obj = cls.__new__(cls)

                setattr(obj, "Name", name)
                setattr(obj, "ObjType", row.objtype)
                setattr(obj, "ChangedBy", row.changedby)
                setattr(obj, "LastUpdated", row.timestamp)

                obj.from_json(row.data)

            if not strict:
                # --- we always  want to cache the object based on its actual
                #     archive date
                date = Date.parse(row.date)

            self[(name, date)] = obj
            return obj

    ##-------------------------------------------------------------------------
    def update_dated(self, obj, date, overwrite=False):
        curs = self.conn.cursor()

        # --- check whether the date in the object matches the timestamp
        if date != obj.LastUpdated:
            ObjDbError("Inconsistent dates for {0!s}: date is {1!s}, "
                       "LastUpdated is {2!s}".format(obj.Name, date,
                                                     obj.LastUpdated))

        # --- check whether the dated object exists
        query = """SELECT Name FROM Archive
                   WHERE Name=%s AND Date=%s LIMIT 1;"""
        curs.execute(query, (obj.Name, date))
        if curs.fetchone() is None:
            raise ObjNotFound("Archived object '{0!s}' not found in {1!s} "
                              "for date {2!s}".format(obj.Name,
                                                      self.dbname, date))

        if not overwrite:
            # --- check if trying to update an object archived in the past
            if date < Date.today():
                raise ObjDbError("Trying to update an "
                                 "archived object without permissions")

        # --- update time-stamp and version on the object
        obj.LastUpdated = Date.now()
        obj.ChangedBy = USER.upper()

        # --- serialize object and create record
        record = (obj.ChangedBy,
                  obj.LastUpdated, obj.to_json(), obj.Name, date)

        # --- DB Insert
        try:
            curs.execute("""UPDATE Archive
                            SET ChangedBy = %s, TimeStamp = %s, Data = %s
                            WHERE Name = %s AND Date = %s;""", record)
        except psql.IntegrityError as err:
            if psql_err.lookup(err.pgcode) == "UNIQUE_VIOLATION":
                raise ObjExists("Dated Object {0!s}-{1!s} already in "
                                "{2!s}".format(obj.Name, date, self.dbname))
            else:
                raise ObjDbError("{0!s}. Name = {1!s}, date = "
                                 "{2!s}".format(err.message, obj.Name, date))
        finally:
            curs.close()

        self[(obj.Name, date)] = obj
        return obj


###############################################################################
class ObjDbDummyClient(ObjDbBase):
    """
    A dummy client that never queries the database backend.
    """
    ##-------------------------------------------------------------------------
    def restart(self):
        pass

    ##-------------------------------------------------------------------------
    def close(self):
        pass

    ##-------------------------------------------------------------------------
    def add(self, obj):
        if obj.Name in self:
            raise ObjExists("Object {0!s} already "
                            "in {1!s}".format(obj.Name, self.dbname))
        self[obj.Name] = obj
        return obj

    ##-------------------------------------------------------------------------
    def get(self, name, refresh=False):
        if refresh:
            raise ObjDbError("get method of "
                             "ObjDbDummyClient does not support refresh")
        try:
            return self[name]
        except KeyError:
            raise ObjNotFound("Object '{0!s}' "
                              "not found in {1!s}".format(name, self.dbname))

    ##-------------------------------------------------------------------------
    def update(self, obj):
        try:
            self[obj.Name] = obj
        except KeyError:
            raise ObjNotFound("Object '{0!s}' not "
                              "found in {1!s}".format(obj.Name, self.dbname))
        return obj

    ##-------------------------------------------------------------------------
    def delete(self, obj):
        if hasattr(obj, "delete"):
            obj.delete()
        del self[obj.Name]

    ##-------------------------------------------------------------------------
    def add_dated(self, obj, date):
        self[(obj.Name, date)] = obj
        return obj

    ##-------------------------------------------------------------------------
    def get_dated(self, name, date, strict=False):
        try:
            return self[(name, date)]
        except KeyError:
            raise ObjNotFound("Archived object '{0!s}' not "
                              "found for date {1!s}".format(name, date))

    ##-------------------------------------------------------------------------
    def update_dated(self, obj, date, override=False):
        self[(obj.Name, date)] = obj
        return obj

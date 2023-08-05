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
"""
Implements base and meta classes for universal financial objects (UFOs) and all
persistable fields.
"""

from onyx.datatypes.date import Date

import getpass
import json
import copy

__all__ = ["UfoBase"]

USER = getpass.getuser()
SPECIAL = ("Name", "ObjType", "Version",
           "ChangedBy", "TimeCreated", "LastUpdated")
SKIP = {"_data", "_json_fields"}.union(SPECIAL)


###############################################################################
class custom_encoder(json.JSONEncoder):
    ##-------------------------------------------------------------------------
    def default(self, obj):
        if isinstance(obj, Date):
            return {
                "__type__": "Date",
                "year": obj.year,
                "month": obj.month,
                "day": obj.day,
                "hour": obj.hour,
                "minute": obj.minute,
                "second": obj.second,
                "microsecond": obj.microsecond,
            }
        # --- let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


###############################################################################
class custom_decoder(json.JSONDecoder):
    ##-------------------------------------------------------------------------
    def __init__(self, *args, **kdws):
        super().__init__(*args, object_hook=self.dict_to_object, **kdws)

    ##-------------------------------------------------------------------------
    def dict_to_object(self, date):
        try:
            typename = date.pop("__type__")
        except KeyError:
            return date
        if typename == "Date":
            return Date(**date)
        else:
            # --- put this back together
            date["__type__"] = typename
            return date


###############################################################################
class FieldError(Exception):
    pass


###############################################################################
class BaseField(object):
    ##-------------------------------------------------------------------------
    def __init__(self, default=None):
        if default is not None:
            self.validate(default)
        self.name = None
        self.default = default

    ##-------------------------------------------------------------------------
    def __get__(self, instance, cls):
        if instance is None:
            return self
        try:
            return instance._data[self.name]
        except KeyError:
            instance._data[self.name] = self.default
            return self.default

    ##-------------------------------------------------------------------------
    def __set__(self, instance, val):
        self.validate(val)
        instance._data[self.name] = val

    ##-------------------------------------------------------------------------
    def from_json(self, val):
        """
        This method is used to prepare the fild value for json reverse
        serialization (needed for data types that are not naturally supported
        by json format).
        """
        return val

    ##-------------------------------------------------------------------------
    def to_json(self, val):
        """
        This method is used to prepare the fild value for json serialization
        (needed for data types that are not naturally supported by json
        format).
        """
        return val

    ##-------------------------------------------------------------------------
    def validate(self, val):
        pass

    ##-------------------------------------------------------------------------
    def __repr__(self):
        return "{0:s} {1!s}".format(self.__class__.__name__, self.name)


###############################################################################
class MutableField(BaseField):
    pass


###############################################################################
class UfoError(Exception):
    pass


###############################################################################
class UfoMetaClass(type):
    ##-------------------------------------------------------------------------
    def __new__(mcl, name, bases, nmspc):
        if "__init__" in nmspc:
            raise UfoError("Classes derived from UfoBase"
                           "cannot implement the __init__ method")

        json_flds = set()

        # --- inherit Instreams of all UFO bases (if any)
        for base in bases:
            if hasattr(base, "_json_fields"):
                json_flds.update(base._json_fields)

        # --- add class specific Instreams and set their name
        for attr_name, attr in nmspc.items():
            if isinstance(attr, BaseField):
                json_flds.add(attr_name)
                attr.name = attr_name

        # --- Instreams is a set with the list of persisted attributes
        nmspc["Instreams"] = json_flds.union(SPECIAL)

        # --- json_flds is a special attribute
        nmspc["_json_fields"] = json_flds

        return super().__new__(mcl, name, bases, nmspc)

    ##-------------------------------------------------------------------------
    ##  class instantiation
    def __call__(cls, *args, **kwds):
        if len(args):
            raise UfoError("Classes derived from UfoBase cannot "
                           "be instantiated with positional arguments")

        # --- create an instance of the class
        instance = cls.__new__(cls)

        for field_name in instance._json_fields:
            field = getattr(cls, field_name)
            if isinstance(field, MutableField) and field.default is not None:
                setattr(instance, field_name, copy.deepcopy(field.default))

        now = Date.now()

        # --- special attributes have default values
        setattr(instance, "Name", kwds.pop("Name", None))
        setattr(instance, "ObjType", kwds.pop("ObjType", cls.__name__))
        setattr(instance, "Version", kwds.pop("Version", 0))
        setattr(instance, "ChangedBy", kwds.pop("ChangedBy", USER))
        setattr(instance, "TimeCreated", kwds.pop("TimeCreated", now))
        setattr(instance, "LastUpdated", kwds.pop("LastUpdated", now))

        for attr, val in kwds.items():
            if attr in instance._json_fields:
                setattr(instance, attr, val)
            else:
                raise UfoError("Unrecognized Instream: {0:s}".format(attr))

        # --- call post-initialization method if available
        if hasattr(cls, "__post_init__"):
            instance.__post_init__()

        return instance


###############################################################################
class UfoBase(metaclass=UfoMetaClass):
    ##-------------------------------------------------------------------------
    def __new__(cls, *args, **kwds):
        instance = super().__new__(cls, *args, **kwds)
        instance._data = {}
        return instance

    ##-------------------------------------------------------------------------
    def to_json(self):
        if self.Name == "":
            raise UfoError("Name attribute cannot be an empty string")

        cls = self.__class__

        # --- create json object
        json_data = {name: getattr(cls, name).to_json(getattr(self, name))
                     for name in self._json_fields}

        return json.dumps(json_data, cls=custom_encoder)

    ##-------------------------------------------------------------------------
    def from_json(self, values):
        cls = self.__class__
        for name, value in json.loads(values, cls=custom_decoder).items():
            self._data[name] = getattr(cls, name).from_json(value)

    ##-------------------------------------------------------------------------
    def __eq__(self, other):
        self_attrs = self.Instreams.difference(SKIP)
        other_attrs = other.Instreams.difference(SKIP)

        if self_attrs != other_attrs:
            return False

        for attr in self_attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    ##-------------------------------------------------------------------------
    def __repr__(self):
        return "<{0:s} {1!s}>".format(self.ObjType, self.Name)

    ##-------------------------------------------------------------------------
    def clone(self, name=None):
        """
        Create a new copy of current object.
        """
        # --- create timestamp
        now = Date.now()

        # --- create a new instrance from current instreams and overwrite the
        #     special attributes
        instreams = {attr: copy.deepcopy(getattr(self, attr))
                     for attr in self.Instreams}
        instreams.update({
            "Name": name,
            "Version": 0,
            "TimeCreated": now,
            "LastUpdated": now,
            "ChangedBy": USER.upper(),
        })

        return self.__class__(**instreams)

    ##-------------------------------------------------------------------------
    def copy_from(self, other):
        """
        Overwrite all attributes with those of another instance.
        """
        if self.ObjType != other.ObjType:
            raise TypeError("Can only copy from an object of the same type")
        for attr in other.Instreams:
            if attr in SKIP:
                continue
            setattr(self, attr, getattr(other, attr))

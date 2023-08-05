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
from onyx.database.objdb_api import ObjDbQuery, GetObj
from onyx.database.ufo_base import BaseField, MutableField, FieldError
from onyx.datatypes.date import Date
from onyx.datatypes.curve import Curve, Knot
from onyx.datatypes.gcurve import GCurve, GKnot
from onyx.datatypes.hlocv import HlocvCurve, HlocvKnot
from onyx.datatypes.structure import Structure
from onyx.datatypes.table import Table
from onyx.datatypes.holiday_calendar import HolidayCalendar

import pickle
import numbers

__all__ = [
    "StringField",
    "SelectField",
    "IntField",
    "SelectIntField",
    "FloatField",
    "BoolField",
    "DateField",
    "ListField",
    "DictField",
    "SetField",
    "CurveField",
    "GCurveField",
    "HlocvCurveField",
    "StructureField",
    "HolidayCalField",
    "ReferenceField",
]


###############################################################################
class StringField(BaseField):
    def validate(self, val):
        if not isinstance(val, str):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class SelectField(StringField):
    def __init__(self, *args, **kwds):
        self.options = kwds.pop("options", None)
        super().__init__(*args, **kwds)
        if not all([isinstance(opt, str) for opt in self.options]):
            types = [type(opt) for opt in self.options]
            raise FieldError("One or more optins are not "
                             "of type str: {0!s}".format(types))

    def validate(self, val):
        super().validate(val)
        if not val in self.options:
            raise FieldError("Illegal value {0!s}. Valid options "
                             "are {1!s}".format(val, self.options))


###############################################################################
class IntField(BaseField):
    def validate(self, val):
        if not isinstance(val, int):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class SelectIntField(IntField):
    def __init__(self, *args, **kwds):
        self.options = kwds.pop("options", None)
        super().__init__(*args, **kwds)
        if not all([isinstance(opt, int) for opt in self.options]):
            types = [type(opt) for opt in self.options]
            raise FieldError("One or more optins are not "
                             "of type int: {0!s}".format(types))

    def validate(self, val):
        super().validate(val)
        if not val in self.options:
            raise FieldError("Illegal value {0!s}. Valid options "
                             "are {1!s}".format(val, self.options))


###############################################################################
class FloatField(BaseField):
    def validate(self, val):
        if not isinstance(val, float):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class BoolField(BaseField):
    def validate(self, val):
        if not isinstance(val, bool):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class DateField(BaseField):
    def from_json(self, val):
        return Date.parse(val)

    def to_json(self, val):
        return val.isoformat()

    def validate(self, val):
        if not isinstance(val, Date):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class ListField(MutableField):
    def validate(self, val):
        if not isinstance(val, list):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class DictField(MutableField):
    def validate(self, val):
        if not isinstance(val, dict):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class SetField(MutableField):
    def from_json(self, val):
        return set(val)

    def to_json(self, val):
        return list(val)

    def validate(self, val):
        if not isinstance(val, set):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class CurveField(MutableField):
    def from_json(self, val):
        crv = Curve.__new__(Curve)
        crv.knot_cls = Knot
        crv.data = [Knot(Date.parse(row["date"]), row["value"]) for row in val]
        return crv

    def to_json(self, crv):
        return [{"date": knt.date.isoformat(),
                 "value": knt.value} for knt in crv]

    def validate(self, val):
        if not isinstance(val, Curve):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class GCurveField(MutableField):
    def from_json(self, val):
        crv = GCurve.__new__(GCurve)
        crv.knot_cls = GKnot
        crv.data = [GKnot(Date.parse(d), pickle.loads(v)) for d, v in val]
        return crv

    def to_json(self, crv):
        return [{"date": knt.date.isoformat(),
                 "value": pickle.dumps(knt.value)} for knt in crv]

    def validate(self, val):
        if not isinstance(val, GCurve):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class HlocvCurveField(MutableField):
    def from_json(self, val):
        crv = HlocvCurve.__new__(HlocvCurve)
        crv.knot_cls = HlocvKnot
        crv.data = [HlocvKnot(Date.parse(d),
                              [float(v) for v in vls]) for d, vls in val]
        return crv

    def to_json(self, crv):
        return [{"date": knt.date.isoformat(),
                 "value": knt.value} for knt in crv]

    def validate(self, val):
        if not isinstance(val, HlocvCurve):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class StructureField(MutableField):
    def from_json(self, val):
        return Structure(val)

    def to_json(self, val):
        return zip(val.keys(), val.values())

    def validate(self, val):
        if not isinstance(val, Structure):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))
        # --- all keys should be strings
        if not all(isinstance(k, str) for k in val.keys()):
            FieldError("Structure keys need to be strings")
        # --- all values should be numbers
        if not all(isinstance(v, numbers.Number) for v in val.values()):
            FieldError("Structure values need to be numbers")


###############################################################################
class TableField(MutableField):
    def from_json(self, val):
        return pickle.loads(val)

    def to_json(self, val):
        return pickle.dumps(val)

    def validate(self, val):
        if not isinstance(val, Table):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class HolidayCalField(MutableField):
    def from_json(self, val):
        return HolidayCalendar([Date.parse(d) for d in val])

    def to_json(self, val):
        return [d.isoformat() for d in val.holidays]

    def validate(self, val):
        if not isinstance(val, HolidayCalendar):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class ReferenceField(StringField):
    def __init__(self, *args, **kwds):
        self.obj_type = kwds.pop("obj_type", None)
        super().__init__(*args, **kwds)

    def validate(self, val):
        if not isinstance(val, str):
            raise FieldError("Invalid input {0!s} "
                             "for <{1!r}>".format(type(val), self))
        if self.obj_type is None:
            res = ObjDbQuery("""SELECT EXISTS "
                                (SELECT 1 FROM Objects
                                 WHERE ObjName=%s) AS "exists";""",
                             parms=(val,), attr="fetchone")
            if res.exists:
                raise FieldError("Object {0:s} "
                                 "not found in database".format(val))
        else:
            try:
                obj = GetObj(val)
            except ObjNotFound:
                raise FieldError("Object {0:s} of type {1:s} not found "
                                 "in database".format(val, self.obj_type))

            bases = [obj.__class__.__name__]
            bases += [cls.__name__ for cls in obj.__class__.__bases__]

            if not self.obj_type in bases:
                raise FieldError("Object {0:s} of type {1:s} not found "
                                 "in database".format(val, self.obj_type))

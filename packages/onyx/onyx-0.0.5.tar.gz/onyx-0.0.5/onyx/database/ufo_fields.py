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

from onyx.database.objdb_api import ObjDbQuery
from onyx.database.ufo_base import (BaseField, FieldError,
                                    custom_decoder, custom_encoder)
from onyx.datatypes.date import Date
from onyx.datatypes.curve import Curve, Knot
from onyx.datatypes.gcurve import GCurve, GKnot
from onyx.datatypes.hlocv import HlocvCurve, HlocvKnot
from onyx.datatypes.structure import Structure
from onyx.datatypes.table import Table
from onyx.datatypes.holiday_calendar import HolidayCalendar


import json
import pickle
import numbers

__all__ = [
    "FieldError",
    "StringField",
    "IntField",
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
    def from_json(self, val):
        return str(json.loads(val))

    def validate(self, val):
        if not isinstance(val, str):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class IntField(BaseField):
    def validate(self, val):
        if not isinstance(val, int):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class FloatField(BaseField):
    def validate(self, val):
        if not isinstance(val, float):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class BoolField(BaseField):
    def validate(self, val):
        if not isinstance(val, bool):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class DateField(BaseField):
    def from_json(self, val):
        return Date.parse(json.loads(val))

    def to_json(self, val):
        return json.dumps(val.isoformat())

    def validate(self, val):
        if not isinstance(val, Date):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class ListField(BaseField):
    def from_json(self, val):
        return set(json.loads(val, cls=custom_decoder))

    def to_json(self, val):
        return json.dumps(val, cls=custom_encoder)

    def validate(self, val):
        if not isinstance(val, list):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class DictField(BaseField):
    def from_json(self, val):
        return set(json.loads(val, cls=custom_decoder))

    def to_json(self, val):
        return json.dumps(val, cls=custom_encoder)

    def validate(self, val):
        if not isinstance(val, dict):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class SetField(BaseField):
    def from_json(self, val):
        return set(json.loads(val, cls=custom_decoder))

    def to_json(self, val):
        return json.dumps(list(val), cls=custom_encoder)

    def validate(self, val):
        if not isinstance(val, set):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class CurveField(BaseField):
    def from_json(self, val):
        crv = Curve.__new__(Curve)
        crv.knot_cls = Knot
        crv.data = [Knot(Date.parse(row["date"]),
                         row["value"]) for row in json.loads(val)]
        return crv

    def to_json(self, crv):
        return json.dumps([{"date": knt.date.isoformat(),
                            "value": knt.value} for knt in crv])

    def validate(self, val):
        if not isinstance(val, Curve):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class GCurveField(BaseField):
    def from_json(self, val):
        crv = GCurve.__new__(GCurve)
        crv.knot_cls = GKnot
        crv.data = [GKnot(Date.parse(d), pickle.loads(v))
                    for d, v in json.loads(val)]
        return crv

    def to_json(self, crv):
        return json.dumps([{"date": knt.date.isoformat(),
                            "value": pickle.dumps(knt.value)} for knt in crv])

    def validate(self, val):
        if not isinstance(val, GCurve):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class HlocvCurveField(BaseField):
    def from_json(self, val):
        crv = HlocvCurve.__new__(HlocvCurve)
        crv.knot_cls = HlocvKnot
        crv.data = [HlocvKnot(Date.parse(d), [float(v) for v in vls])
                    for d, vls in json.loads(val)]
        return crv

    def to_json(self, crv):
        return json.dumps([{"date": knt.date.isoformat(),
                            "value": knt.value} for knt in crv])

    def validate(self, val):
        if not isinstance(val, HlocvCurve):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class StructureField(BaseField):
    def from_json(self, val):
        return Structure(json.loads(val), cls=custom_decoder)

    def to_json(self, val):
        return json.dumps(zip(val.keys(), val.values()), cls=custom_encoder)

    def validate(self, val):
        if not isinstance(val, Structure):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))
        # --- all keys should be strings
        if not all(isinstance(k, str) for k in val.keys()):
            FieldError("Structure keys need to be strings")
        # --- all values should be numbers
        if not all(isinstance(v, numbers.Number) for v in val.values()):
            FieldError("Structure values need to be numbers")


###############################################################################
class TableField(BaseField):
    def from_json(self, val):
        return pickle.loads(json.loads(val))

    def to_json(self, val):
        return json.dumps(pickle.dumps(val))

    def validate(self, val):
        if not isinstance(val, Table):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class HolidayCalField(BaseField):
    def from_json(self, val):
        return HolidayCalendar([Date.parse(d) for d in json.loads(val)])

    def to_json(self, val):
        return json.dumps([d.isoformat() for d in val.holidays])

    def validate(self, val):
        if not isinstance(val, HolidayCalendar):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))


###############################################################################
class ReferenceField(StringField):
    def __init__(self, *args, **kwds):
        self.obj_type = kwds.pop("obj_type", None)
        super().__init__(*args, **kwds)

    def validate(self, val):
        if not isinstance(val, str):
            raise FieldError("Invalid input {0:s} "
                             "for <{1!r}>".format(type(val), self))
        if self.obj_type is None:
            res = ObjDbQuery("SELECT 1 FROM Objects WHERE ObjName=%s "
                             "LIMIT 1;", parms=(val,), attr="fetchone")
            if res is None:
                raise FieldError("Object {0:s} "
                                 "not found in database".format(val))
        else:
            res = ObjDbQuery("SELECT 1 FROM Objects "
                             "WHERE ObjName=%s AND ObjType=%s LIMIT 1;",
                             parms=(val, self.obj_type), attr="fetchone")
            if res is None:
                raise FieldError("Object %s of type {0:s} not found "
                                 "in database".format(val, self.obj_type))

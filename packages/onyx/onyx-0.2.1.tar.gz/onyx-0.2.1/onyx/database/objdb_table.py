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

from onyx.datatypes.table import row_factory, Table
from onyx.database.ufo_base import UfoBase
from onyx.database.ufo_fields import TableField, DictField
from onyx.database.objdb_api import ObjDbQuery

__all__ = ["TableSchema", "ObjDbTable"]

TAGS = ("column_name", "data_type", "column_constraint")
ROW_CLS = row_factory(TAGS)


###############################################################################
class TableSchema(Table):
    # -------------------------------------------------------------------------
    def __init__(self, schema):
        self.tags = TAGS
        self.row_fmt = "{0:20s}  {1:20s}  {2:20s}"
        self.row_cls = ROW_CLS
        self.data = [ROW_CLS(row) for (i, row) in enumerate(schema)]


###############################################################################
class ObjDbTable(UfoBase):
    """
    This UFO class is used to crerate and manage backend database tables.
    """
    Schema = TableField()
    Unique = DictField({})
    Indexes = DictField({})

    # -------------------------------------------------------------------------
    def __post_init__(self):
        # --- validate indexes
        for index_name, index_columns in self.Indexes.items():
            if not set(index_columns).issubset(self.columns):
                raise ValueError("Index {0:s} is not valid (some "
                                 "of the columns are not defined "
                                 "for this table's schema)".format(index_name))

    # -------------------------------------------------------------------------
    @property
    def columns(self):
        return [row.column_name for row in self.Schema]

    # -------------------------------------------------------------------------
    @property
    def __create_table(self):
        col_fmt = "    {0:s},\n"
        sql = ["CREATE TABLE {0:s} (\n".format(self.Name)]
        for entry in self.Schema:
            sql.append(col_fmt.format(" ".join(entry.str_values).rstrip()))

        for constr_name, constr_columns in self.Unique.items():
            columns = ",".join(constr_columns)
            sql.append("    CONSTRAINT {0:s} UNIQUE "
                       "({1:s}),\n".format(constr_name, columns))

        # --- strip the last comma
        sql[-1] = sql[-1].replace(",\n", "\n")

        sql.append(");")
        return "".join(sql)

    # -------------------------------------------------------------------------
    @property
    def __create_indexes(self):
        sql = []
        for index_name, index_columns in self.Indexes.items():
            columns = ",".join(index_columns)
            sql.append("CREATE INDEX {0:s} ON {1:s} "
                       "({2:s});\n".format(index_name, self.Name, columns))
        return "".join(sql)

    # -------------------------------------------------------------------------
    def create(self):
        ObjDbQuery(self.__create_table)
        ObjDbQuery(self.__create_indexes)

    # -------------------------------------------------------------------------
    def delete(self):
        # --- drop table from backend
        ObjDbQuery("DROP TABLE IF EXISTS {0:s} CASCADE;".format(self.Name))


if __name__ == "__main__":
    schema = TableSchema([
        ["TradeDate", "date", "NOT NULL"],
        ["TimeCreated", "timestamptz", "NOT NULL"],
        ["Book", "varchar(64)", "NOT NULL"],
        ["Trader", "varchar(64)", "NOT NULL"],
        ["Qty", "double precision", "NOT NULL"],
        ["Unit", "varchar(64)", "NOT NULL"],
        ["UnitType", "varchar(64)", "NOT NULL"],
        ["Status", "char(1)", "NOT NULL"],
        ["Trade", "varchar(64)", "NOT NULL"],
        ["DealId", "varchar(64)", "NOT NULL"],
        ["NTD", "date", ""]
    ])

    unique = {
        "tarde_and_status": ["Trade", "Status"],
    }

    indexes = {
        "pos_by_trade_date": ["TradeDate"],
        "pos_by_time_created": ["TimeCreated"],
        "pos_by_book": ["Book"],
        "pos_by_trader": ["Trader"],
        "pos_by_trade": ["DealId"],
        "pos_by_ntd": ["NTD"],
    }

    table = ObjDbTable(Name="PosEffects", Schema=schema,
                       Unique=unique, Indexes=indexes)

    print(table._ObjDbTable__create_table)

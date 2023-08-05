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

from onyx.database.ufo_base import UfoBase
from onyx.database.ufo_fields import IntField, FloatField, StringField
from onyx.depgraph.graph_api import GraphNodeVt

import time

__all__ = []


class TestCls0(UfoBase):
    def test_method(self, arg):
        return arg


class TestCls1(UfoBase):
    attr1 = IntField(default=333)
    attr2 = IntField(default=666)

    @GraphNodeVt("Property")
    def A(self, graph):
        return 1.0 + graph(self, "B") + graph(self, "C", 1, 2)

    @GraphNodeVt()
    def B(self, graph):
        # --- this is a slow method
        time.sleep(2.0)
        return graph(self, "attr1")

    @GraphNodeVt()
    def C(self, graph, x, y=0):
        # --- this is a slow calculated method
        time.sleep(2.0)
        return x + y + graph(self, "attr2")


class TestCls2(UfoBase):
    Kid1 = StringField()
    Kid2 = StringField()

    @GraphNodeVt()
    def A(self, graph):
        kid1 = graph(self, "Kid1")
        kid2 = graph(self, "Kid2")
        return graph(kid1, "A") + graph(kid2, "A")


class TestCls3(UfoBase):
    Number = FloatField(default=666.0)

    @GraphNodeVt("Property")
    def CalcProperty(self, graph):
        return 1.0 + 2.0*graph(self, "Number")

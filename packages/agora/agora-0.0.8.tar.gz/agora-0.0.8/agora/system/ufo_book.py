###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
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

from onyx.core import (Structure, UfoBase, ReferenceField, StringField,
                       GraphNodeVt)

from agora.corelibs.trade_api import ChildrenByBook

__all__ = ["Book"]


###############################################################################
class Book(UfoBase):
    """
    Class used to represent a trading books (either internal or external).
    """
    Account = StringField()
    Owner = ReferenceField(obj_type="Trader")
    Description = StringField()
    Denominated = ReferenceField(default="USD", obj_type="Currency")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Children(self, graph):
        pos_dt = graph("Database", "PositionsDate")
        return ChildrenByBook(graph(self, "Name"), pos_dt)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        leaves = Structure()
        for child, qty in graph(self, "Children").items():
            leaves += qty*graph(child, "Leaves")
        return leaves

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        mtm = 0.0
        for leaf, qty in graph(self, "Leaves").items():
            mtm += qty*graph(leaf, "MktValUSD")
        return mtm

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        denominated = graph(self, "Denominated")
        spot_fx = graph("{0:3s}/USD".format(denominated, "Spot"))
        return graph(self, "MktValUSD") / spot_fx

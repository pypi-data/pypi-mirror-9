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

from onyx.core import (GraphNodeVt, UfoBase,
                       ReferenceField, StringField, ObjDbQuery)

from agora.risk.core_functions import WithRiskValueTypes

import json

__all__ = ["Group"]

GET_ITEMS = "SELECT Name FROM Objects WHERE ObjType=Trader AND Data @> %s;"


###############################################################################
@WithRiskValueTypes
class Group(UfoBase):
    """
    Class used to represent a Portfolio (i.e. a collection of books or other
    sub-portfolios).
    """
    Portfolio = ReferenceField(obj_type="Portfolio")
    LongName = StringField()

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        return graph(graph(self, "Portfolio"), "Leaves")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        return graph(graph(self, "Portfolio"), "MktValUSD")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        return graph(graph(self, "Portfolio"), "MktVal")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Traders(self, graph):
        parms = (json.dumps({"Group": graph(self, "Name")}), )
        results = ObjDbQuery(GET_ITEMS, parms, attr="fetchall")
        return sorted([res.name for res in results])


# -----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.unittest_utils import AddIfMissing
    import agora.system.ufo_portfolio as ufo_portfolio

    portfolios = ufo_portfolio.prepare_for_test()

    groups = [
        AddIfMissing(Group(Name="TEST_GROUP", Portfolio=portfolios[0]))
    ]

    return [group.Name for group in groups]

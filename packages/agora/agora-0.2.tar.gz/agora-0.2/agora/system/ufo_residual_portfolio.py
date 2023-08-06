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

from onyx.core import Structure, GraphNodeVt, UfoBase, ReferenceField

from agora.corelibs.ufo_functions import InheritAsProperty
from agora.risk.core_functions import WithRiskValueTypes

__all__ = ["ResidualPortfolio"]


###############################################################################
@WithRiskValueTypes
@InheritAsProperty(["Denominated", "Children"], "RefPortfolio")
class ResidualPortfolio(UfoBase):
    """
    Based on a reference portfolio (RefPortfolio), this class represents what
    is left of such portfolio once all leaves that are present in a reference
    category object (RefCategory) have been removed.
    Typical use is in the calculation of marginal Value At Risk.
    """
    RefPortfolio = ReferenceField(obj_type="Portfolio")
    RefCategory = ReferenceField(obj_type="Category")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        exclude_items = graph(graph(self, "RefCategory"), "Items")
        leaves = Structure()
        for child, qty in graph(self, "Children").items():
            leaves += qty*graph(child, "Leaves")
        return Structure({leaf: qty for leaf, qty in leaves.items()
                          if leaf not in exclude_items})

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        mtm = 0.0
        for leaf, qty in graph(self, "Leaves").items():
            mtm += qty*graph(leaf, "MktValUSD")
        return mtm

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        denominated = graph(self, "Denominated")
        spot_fx = graph("{0:3s}/USD".format(denominated, "Spot"))
        return graph(self, "MktValUSD") / spot_fx

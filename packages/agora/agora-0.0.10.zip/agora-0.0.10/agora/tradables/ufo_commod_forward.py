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

from onyx.core import (GetVal, GraphNodeVt,
                       IntField, DateField, SelectField, ReferenceField)

from agora.corelibs.tradable_api import (FwdTradableObj,
                                         AddByInference, HashInstreams)
from agora.tradables.ufo_commod_nrby import AVERAGING_TYPES, CommodNrby

__all__ = ["CommodForward"]


###############################################################################
class CommodForward(FwdTradableObj):
    """
    Tradable class that represents the floating leg of a commodity forward
    contract that is settled in cash.
    """
    Asset = ReferenceField(obj_type="CommodAsset")
    AvgStartDate = DateField()
    AvgEndDate = DateField()
    AvgType = SelectField(options=AVERAGING_TYPES)
    RollType = IntField(default=0)
    Denominated = ReferenceField(obj_type="Currency")

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        # --- set defaults for attributes inherited from Asset
        for attr in ["Denominated"]:
            if getattr(self, attr) is None:
                setattr(self, attr, GetVal(self.Asset, attr))

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Nearby(self, graph):
        # --- create the nearby object in memory
        info = {
            "Asst": graph(self, "Asset"),
            "StartDate": graph(self, "AvgStartDate"),
            "EndDate": graph(self, "AvgEndDate"),
            "AvgType": graph(self, "AvgType"),
            "RollType": graph(self, "RollType"),
        }
        nrby = AddByInference(CommodNrby(**info), in_memory=True)
        return graph(nrby, "Name")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def UndiscountedValue(self, graph):
        return graph(graph(self, "Nearby"), "AverageValue")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        pd = graph("Database", "PricingDate")
        ed = graph(self, "ExpirationDate")
        ccy = graph(self, "Denominated")
        df = graph(ccy, "DiscountFactor", ed, pd)
        return df*graph(self, "UndiscountedValue")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def UndiscountedValueUSD(self, graph):
        # --- fx conversion
        fx = graph("{0:3s}/USD".format(graph(self, "Denominated")), "Spot")
        return fx*graph(self, "UndiscountedValue")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        fx = graph("{0:3s}/USD".format(graph(self, "Denominated")), "Spot")
        return fx*graph(self, "MktVal")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpirationDate(self, graph):
        return graph(self, "AvgEndDate")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionDate(self, graph):
        return graph(self, "ExpirationDate")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionEvent(self, graph):
        return "Expire"

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionSecurity(self, graph):
        return None

    ##-------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        mkt = GetVal(self.Asset, "Market")
        sym = GetVal(self.Asset, "Symbol")
        return "CmdFWD {0:s} {1:s} {2:8s} " \
               "{{0:2d}".format(mkt, sym, HashInstreams(self, 8))

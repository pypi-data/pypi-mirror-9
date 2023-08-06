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

from onyx.core import (Structure, GraphNodeVt, GetVal,
                       IntField, FloatField, StringField, ReferenceField)

from agora.corelibs.tradable_api import (FwdTradableObj,
                                         AddByInference, HashInstreams)

from agora.tradablas.ufo_commod_forward import CommodForward
from agora.tradables.ufo_forward_cash import ForwardCash


###############################################################################
class CommodFutures(FwdTradableObj):
    """
    Tradable class that represents a commodity futures contract.
    """
    Asset = ReferenceField(obj_type="CommodAsset")
    ContractMonth = StringField()
    Quantity = IntField()
    FixedPrice = FloatField()
    Denominated = ReferenceField(obj_type="Currency")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        cnt_mth = graph(self, "ContractMonth")
        qty = graph(self, "Quantity")

        fwd_info = {
            "Asset": graph(self, "Asset"),
            "AvgStartDate": cnt_mth,
            "AvgEndDate": cnt_mth,
            "AvgType": "LAST",
        }
        cash_info = {
            "Currency": graph(self, "Denominated"),
            "PaymentDate": graph(self, "ExpirationDate"),
        }

        fwd_sec = AddByInference(CommodForward(**fwd_info), True)
        cash_sec = AddByInference(ForwardCash(**cash_info), True)

        # --- use list-based constructor to enforce key ordering
        return Structure([
            (fwd_sec.Name,  qty),
            (cash_sec.Name, -qty*graph(self, "FixedPrice"))
        ])

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def UndiscountedValue(self, graph):
        fx = graph("{0:3s}/USD".format(graph(self, "Denominated")), "Spot")
        return graph(self, "UndiscountedValueUSD") / fx

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        """
        NB: no discounting because this is a Futures contract.
        """
        return graph(self, "UndiscountedValue")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def UndiscountedValueUSD(self, graph):
        val = 0.0
        for sec, qty in graph(self, "Leaves").items():
            val += qty*graph(sec, "UndiscountedValueUSD")
        return val

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        """
        NB: no discounting because this is a Futures contract.
        """
        return graph(self, "UndiscountedValueUSD")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpirationDate(self, graph):
        asset = graph(self, "Asset")
        cnt = graph(asset, "GetContract", graph(self, "ContractMonth"))
        return graph(cnt, "FutSettDate")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionDate(self, graph):
        return graph(self, "ExpirationDate")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionEvent(self, graph):
        return "Settlement"

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionSecurity(self, graph):
        return None

    ##-------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        mkt = GetVal(self.Asset, "Market")
        sym = GetVal(self.Asset, "Symbol")
        cnt = self.ContractMonth
        return "CmdFUT {0:s} {1:s} {2:3s} {3:3s} " \
               "{{0:2d}".format(mkt, sym, cnt, HashInstreams(self, 3))

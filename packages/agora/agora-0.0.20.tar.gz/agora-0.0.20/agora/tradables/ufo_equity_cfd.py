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

from onyx.core import (Structure, GetObj, GraphNodeVt, GetVal, SetVal,
                       FloatField, ReferenceField)

from agora.corelibs.tradable_api import (TradableObj, NamedByInference,
                                         AddByInference, HashInstreams)
from agora.tradables.ufo_cash_balance import CashBalance

__all__ = ["EquityCFD"]


###############################################################################
class EquityFixedLeg(NamedByInference):
    """
    Fixed leg of the CFD.
    """
    Currency = ReferenceField(obj_type="Currency")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        return 1.0

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        return graph("{0:3s}/USD".format(graph(self, "Currency")), "Spot")

    ##-------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        return "EqFixed {0:3s} {{0:2d}}".format(self.Currency)


###############################################################################
class EquityFloatingLeg(NamedByInference):
    """
    Floating leg of the CFD.
    """
    Asset = ReferenceField(obj_type="EquityAsset")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        return graph(graph(self, "Asset"), "Spot")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        den = graph(graph(self, "Asset"), "Denominated")
        fx = graph("{0:3s}/USD".format(den), "Spot")
        return fx*graph(self, "MktVal")

    ##-------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        asset = GetObj(self.Asset)
        exchg = GetObj(asset.Exchange)
        return "EqFloating {0:6s} " \
               "{1:2s} {{0:2d}}".format(asset.Symbol, exchg.Code)


###############################################################################
class EquityCFD(TradableObj):
    """
    Tradable class that represents a contract for difference on a equity asset.
    """
    Asset = ReferenceField(obj_type="EquityAsset")
    FixedPrice = FloatField()
    # --- the settlement currency can differ from the denomination of the asset
    SettlementCcy = ReferenceField(obj_type="Currency")
    # --- fx rate uesd to convert the fixed price (which is expressed in the
    #     currency of the asset) to the settlement currency
    SettlementFx = FloatField()

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def AssetSpot(self, graph):
        return graph(graph(self, "Asset"), "Spot")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        """
        Return a Structure with security names as keys and net quantities as
        values.
        """
        asset = graph(self, "Asset")
        ccy = graph(self, "SettlementCcy")

        # --- leaves are created in memory
        floating = AddByInference(EquityFloatingLeg(Asset=asset), True)
        fixed = AddByInference(EquityFixedLeg(Currency=ccy), True)

        return Structure({
            floating.Name: 1.0,
            fixed.Name: -graph(self, "FixedPrice")*graph(self, "SettlementFx"),
        })

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        mtm = 0.0
        for sec, qty in graph(self, "Leaves").items():
            mtm += qty*graph(sec, "MktValUSD")
        return mtm

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        sett_ccy = graph(self, "SettlementCcy")
        spot_fx = graph("{0:3s}/USD".format(sett_ccy), "Spot")
        return graph(self, "MktValUSD") / spot_fx

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpectedSecurities(self, graph):
        asset = graph(self, "Asset")
        ccy = graph(self, "SettlementCcy")

        floating = AddByInference(EquityFloatingLeg(Asset=asset), True)
        cash = AddByInference(CashBalance(ccy), True)

        return Structure({
            floating.Name: 1.0,
            cash.Name: -graph(self, "FixedPrice")*graph(self, "SettlementFx"),
        })

    ##-------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        asset = GetObj(self.Asset)
        exchg = GetObj(asset.Exchange)
        return "EqCFD {0:6s} {1:2s} {2:3s} {3:4s} " \
               "{{0:2d}}".format(asset.Symbol, exchg.Code,
                                 self.SettlementCcy, HashInstreams(self, 4))


###############################################################################
class EquityCFDCalc(EquityCFD):
    """
    Calculator class.
    """
    PriceAdjust = FloatField(default=0.0)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def TradableFactory(self, graph):
        """
        Return a list of tradables objects that replicate the calculator.
        """
        info = {"Asset": graph(self, "Asset"),
                "FixedPrice": graph(self, "FixedPrice"),
                "SettlementCcy": graph(self, "SettlementCcy"),
                "SettlementFx": graph(self, "SettlementFx")}
        return [EquityCFD(**info)]

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def AssetSpot(self, graph):
        return graph(self, "PriceAdjust") + graph(graph(self, "Asset"), "Spot")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        dnpv = 0.0
        for sec, qty in graph(self, "Leaves").items():
            dnpv += qty*graph(sec, "MktValUSD")
        return dnpv + graph(self, "PriceAdjust")

    ##-------------------------------------------------------------------------
    def spot_settlement_fx(self):
        ccy1 = GetVal(GetVal(self, "Asset"), "Denominated")
        ccy2 = GetVal(self, "SettlementCcy")
        cross1 = "{0:3s}/USD".format(ccy1)
        cross2 = "{0:3s}/USD".format(ccy2)
        fx_rate = GetVal(cross1, "Spot") / GetVal(cross2, "Spot")

        SetVal(self, "SettlementFx", fx_rate)

        return fx_rate

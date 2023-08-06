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

from onyx.core import (Date, Structure, GraphNodeVt, GetVal,
                       FloatField, DateField, ReferenceField)

from agora.corelibs.tradable_api import (TradableObj, NamedByInference,
                                         AddByInference, HashStoredAttrs)
from agora.tradables.ufo_forward_cash import ForwardCash

__all__ = ["EquityCFD"]


###############################################################################
class EquityFixedLeg(NamedByInference):
    """
    Fixed leg of the CFD.
    """
    Currency = ReferenceField(obj_type="Currency")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        return 1.0

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        return graph("{0:3s}/USD".format(graph(self, "Currency")), "Spot")

    # -------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        return "EqFixed {0:3s}".format(self.Currency)


###############################################################################
class EquityFloatingLeg(NamedByInference):
    """
    Floating leg of the CFD.
    """
    Asset = ReferenceField(obj_type="EquityAsset")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        return graph(graph(self, "Asset"), "Spot")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        den = graph(graph(self, "Asset"), "Denominated")
        fx = graph("{0:3s}/USD".format(den), "Spot")
        return fx*graph(self, "MktVal")

    # -------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        sym = GetVal(self.Asset, "Symbol")
        code = GetVal(GetVal(self.Asset, "Exchange"), "Code")
        return "EqFloating {0:s} {1:2s}".format(sym, code)


###############################################################################
class EquityCFD(TradableObj):
    """
    Tradable class that represents a contract for difference on a equity asset.
    """
    Asset = ReferenceField(obj_type="EquityAsset")
    FixedPrice = FloatField(positive=True)

    # --- the settlement currency can differ from the denomination of the asset
    SettlementCcy = ReferenceField(obj_type="Currency")

    # --- fx rate uesd to convert the fixed price (which is expressed in the
    #     currency of the asset) to the settlement currency
    SettlementFx = FloatField()

    # --- last known ex-dividend date: this is used to get a new ImpliedName
    #     every time a dividend is paid (needed by the aging mechanism).
    LastDvdDate = DateField(default=Date.low_date())

    # -------------------------------------------------------------------------
    def __post_init__(self):
        asset_ccy = GetVal(self.Asset, "Denominated")

        self.SettlementCcy = self.SettlementCcy or asset_ccy

        if self.SettlementFx is None:
            # --- default to spot
            if asset_ccy == self.SettlementCcy:
                fx = 1.0
            else:
                asset_cross = "{0:3s}/USD".format(asset_ccy)
                sett_cross = "{0:3s}/USD".format(self.SettlementCcy)
                fx = GetVal(asset_cross, "Spot") / GetVal(sett_cross, "Spot")

            self.SettlementFx = fx

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        """
        Return a Structure with security names as keys and net quantities as
        values.
        """
        asset = graph(self, "Asset")
        ccy = graph(self, "SettlementCcy")

        prc = graph(self, "FixedPrice")
        mul = graph(asset, "Multiplier")
        fx = graph(self, "SettlementFx")

        # --- leaves are created in memory
        floating = AddByInference(EquityFloatingLeg(Asset=asset), True)
        fixed = AddByInference(EquityFixedLeg(Currency=ccy), True)

        return Structure({
            floating.Name: 1.0,
            fixed.Name: -prc*mul*fx,
        })

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        mtm = 0.0
        for sec, qty in graph(self, "Leaves").items():
            mtm += qty*graph(sec, "MktValUSD")
        return mtm

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        sett_ccy = graph(self, "SettlementCcy")
        spot_fx = graph("{0:3s}/USD".format(sett_ccy), "Spot")
        return graph(self, "MktValUSD") / spot_fx

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def GetLastDvdDate(self, graph):
        """
        Return the last known ex-dividend date.
        """
        return graph(graph(self, "Asset"), "GetDividends").back.date

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionDate(self, graph):
        pd = graph("Database", "PricingDate")
        schedule = graph(graph(self, "Asset"), "DividendSchedule")
        return schedule.crop(start=pd).front.date

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def TradeTypes(self, graph):
        mapping = super().TradeTypes
        mapping.update({
            "ExDividend": "ExDividendSecurities",
        })
        return mapping

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpectedTransaction(self, graph):
        return "ExDividend"

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExDividendSecurities(self, graph):
        ccy = graph(graph(self, "Asset"), "Denominated")
        ntd = graph(self, "NextTransactionDate")

        # --- dividend receivable
        schedule = graph(graph(self, "Asset"), "DividendSchedule")
        pay_date = schedule[ntd].PaymentDate
        pay_qty = schedule[ntd].NetDividend
        cash = ForwardCash(Currency=ccy, PaymentDate=pay_date)

        # --- the rolled cfd
        rolled_cfd = self.clone()
        rolled_cfd.LastDvdDate = ntd

        return [
            {"Security": AddByInference(cash, in_memory=True),
             "Quantity": pay_qty},
            {"Security": AddByInference(rolled_cfd, in_memory=True),
             "Quantity": 1.0},
        ]

    # -------------------------------------------------------------------------
    #  this value type is used by edit screens
    @GraphNodeVt("Property")
    def AssetSpot(self, graph):
        return graph(graph(self, "Asset"), "Spot")

    # -------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        sym = GetVal(self.Asset, "Symbol")
        code = GetVal(GetVal(self.Asset, "Exchange"), "Code")
        mush = HashStoredAttrs(self, 4)
        return ("EqCFD {0:s} {1:2s} {2:3s} {3:4s} "
                "{{0:2d}}").format(sym, code, self.SettlementCcy, mush)


###############################################################################
class EquityCFDCalc(EquityCFD):
    """
    Calculator class.
    """
    PriceAdjust = FloatField(default=0.0)

    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def AssetSpot(self, graph):
        return graph(self, "PriceAdjust") + graph(graph(self, "Asset"), "Spot")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        dnpv = 0.0
        for sec, qty in graph(self, "Leaves").items():
            dnpv += qty*graph(sec, "MktValUSD")
        return dnpv + graph(self, "PriceAdjust")

    # -------------------------------------------------------------------------
    def spot_settlement_fx(self):
        ccy1 = GetVal(GetVal(self, "Asset"), "Denominated")
        ccy2 = GetVal(self, "SettlementCcy")
        cross1 = "{0:3s}/USD".format(ccy1)
        cross2 = "{0:3s}/USD".format(ccy2)
        fx_rate = GetVal(cross1, "Spot") / GetVal(cross2, "Spot")

        return fx_rate


# -----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.tradable_api import AddByInference
    import agora.system.ufo_equity_asset as ufo_equity_asset
    import agora.tradables.ufo_forward_cash as ufo_forward_cash

    ufo_equity_asset.prepare_for_test()
    ufo_forward_cash.prepare_for_test()

    info = {
        "Asset": "EQ NG/ LN",
        "FixedPrice": 910.0,
    }

    securities = [AddByInference(EquityCFD(**info))]

    return [sec.Name for sec in securities]

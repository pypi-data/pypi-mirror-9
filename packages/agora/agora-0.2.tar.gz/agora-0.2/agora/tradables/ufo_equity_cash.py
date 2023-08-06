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

from onyx.core import (Date, GraphNodeVt, GetVal,
                       FloatField, DateField, ReferenceField)

from agora.corelibs.tradable_api import (TradableObj,
                                         AddByInference, HashStoredAttrs)
from agora.tradables.ufo_forward_cash import ForwardCash

__all__ = ["EquityCash"]


###############################################################################
class EquityCash(TradableObj):
    """
    Tradable class that represents the ownershi of shares in a company.
    """
    Asset = ReferenceField(obj_type="EquityAsset")

    # --- last known ex-dividend date: this is used to get a new ImpliedName
    #     every time a dividend is paid (needed by the aging mechanism).
    LastDvdDate = DateField(default=Date.low_date())

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
        return "EqCASH {0:s} {1:2s} {2:4s} {{0:2d}}".format(sym, code, mush)


###############################################################################
class EquityCashCalc(EquityCash):
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
        info = {"Asset": graph(self, "Asset")}
        return [EquityCash(**info)]

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
    import agora.system.ufo_currency as ufo_currency
    import agora.system.ufo_currency_cross as ufo_currency_cross
    import agora.system.ufo_equity_asset as ufo_equity_asset

    ufo_currency.prepare_for_test()
    ufo_currency_cross.prepare_for_test()
    ufo_equity_asset.prepare_for_test()

    securities = [AddByInference(EquityCash(Asset="EQ NG/ LN"))]

    return [sec.Name for sec in securities]

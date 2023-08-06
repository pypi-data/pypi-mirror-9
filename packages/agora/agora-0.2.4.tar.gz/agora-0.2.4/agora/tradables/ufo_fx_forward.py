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

from onyx.core import (Structure, GraphNodeVt, ReferenceField,
                       FloatField, BoolField, DateField, StringField)

from agora.corelibs.tradable_api import (AgingTradableObj,
                                         AddByInference, HashStoredAttrs)
from agora.tradables.ufo_forward_cash import ForwardCash
from agora.tradables.ufo_cash_balance import CashBalance


###############################################################################
class FxForward(AgingTradableObj):
    """
    Tradable class that represents a FX forward (in either a deliverable or
    non-deliverable currency).
    """
    # --- this is the currency delivered forward
    CurrencyDel = ReferenceField(obj_type="Currency")

    # --- this is the currency received forward
    CurrencyRec = ReferenceField(obj_type="Currency")

    # --- the agreed forward fx rate: this determines the amount of CurrencyRec
    FxRate = FloatField()

    # --- this represents the delivery date for deliverable forwards and the
    #     fixing date for non-deliverable forwards
    DeliveryDate = DateField()

    # --- False for a non-deliverable forward (NDF). Only affects settlement.
    Deliverable = BoolField(default=True)

    # --- this field is only used for non-deliverable forwards. The relevant
    #     calendar is that of the delivered currency.
    SettDateRule = StringField(default="+2b")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        fwd_ccy1 = ForwardCash(Currency=graph(self, "CurrencyDel"),
                               PaymentDate=graph(self, "DeliveryDate"))
        fwd_ccy1 = AddByInference(fwd_ccy1, in_memory=True)
        fwd_ccy2 = ForwardCash(Currency=graph(self, "CurrencyRec"),
                               PaymentDate=graph(self, "DeliveryDate"))
        fwd_ccy2 = AddByInference(fwd_ccy2, in_memory=True)
        return Structure({
            fwd_ccy1.Name: -1.0,
            fwd_ccy2.Name: graph(self, "FxRate"),
        })

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        mtm_usd = 0.0
        for leaf, qty in graph(self, "Leaves").items():
            mtm_usd += qty*graph(leaf, "MktValUSD")
        return mtm_usd

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        """
        By convenction, the reference currency of an FX Forward is the currency
        that is delivered forward.
        """
        cross = "{0:3s}/USD".format(graph(self, "CurrencyDel"))
        return graph(self, "MktValUSD") / graph(cross, "Spot")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpirationDate(self, graph):
        return graph(self, "DeliverytDate")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionDate(self, graph):
        return graph(self, "DeliverytDate")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def TradeTypes(self, graph):
        mapping = super().TradeTypes
        mapping.update({
            "Settle": "SettleSecurities",
        })
        return mapping

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpectedTransaction(self, graph):
        return "Settle"

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def SettleSecurities(self, graph):
        cash_del = CashBalance(Currency=graph(self, "CurrencyDel"))
        cash_rec = CashBalance(Currency=graph(self, "CurrencyRec"))
        return [
            {"Security": AddByInference(cash_del, in_memory=True),
             "Quantity": -1.0},
            {"Security": AddByInference(cash_rec, in_memory=True),
             "Quantity": graph(self, "FxRate")},
        ]

    # -------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        ccy_del = self.CurrencyDel
        ccy_rec = self.CurrencyRec
        del_date = self.DeliveryDate.strftime("%d%m%y")
        mush = HashStoredAttrs(self, 4)
        return ("FX-FWD {0:3s}/{1:3s} {2:6s} {3:4s} "
                "{{0:2d}}").format(ccy_del, ccy_rec, mush, del_date)


# -----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import Date, RDate
    from agora.corelibs.tradable_api import AddByInference
    import agora.tradables.ufo_forward_cash as ufo_forward_cash

    ufo_forward_cash.prepare_for_test()

    del_date = Date.today() + RDate("+1y")

    securities = []
    for ccy in ["EUR", "GBP"]:
        securities.append(AddByInference(FxForward(CurrencyDel=ccy,
                                                   CurrencyRec="USD",
                                                   FxRate=1.00,
                                                   DeliveryDate=del_date)))

    return [sec.Name for sec in securities]

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

from onyx.core import (Structure, GraphNodeVt, ReferenceField, DateField)

from agora.corelibs.tradable_api import FwdTradableObj, AddByInference
from agora.tradables.ufo_cash_balance import CashBalance


##-----------------------------------------------------------------------------
class ForwardCash(FwdTradableObj):
    """
    Tradable class that represents cash to be exchanged at a future date.
    """
    Currency = ReferenceField(objtype="Currency")
    PaymentDate = DateField()

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def UndiscountedValue(self, graph):
        return 1.0

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        pd = graph("Database", "PricingDate")
        ed = graph(self, "PaymentDate")

        if pd < ed:
            ccy = graph(self, "Currency")
            return graph(ccy, "DiscountFactor", ed, pd)
        else:
            return 1.0

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def UndiscountedValueUSD(self, graph):
        cross = "{0:3s}/USD".format(graph(self, "Currency"))
        return graph(cross, "Spot")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        cross = "{0:3s}/USD".format(graph(self, "Currency"))
        return graph(self, "MktVal")*graph(cross, "Spot")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpirationDate(self, graph):
        return graph(self, "PaymentDate")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionDate(self, graph):
        return graph(self, "PaymentDate")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def NextTransactionEvent(self, graph):
        return "PAY"

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ExpectedSecurities(self, graph):
        cash = AddByInference(CashBalance(graph(self, "Currency")))
        return Structure({cash.Name: 1})

    ##-------------------------------------------------------------------------
    @property
    def ImpliedName(self):
        pay_date = self.PaymentDate.strftime("%d%m%y")
        return "FWD {0:3s} {1:6s} {{0:2d}}".format(self.Currency, pay_date)

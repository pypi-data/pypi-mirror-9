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

from onyx.core import Date, RDate, UfoBase, GraphNodeVt

__all__ = ["Risk"]


###############################################################################
class Risk(UfoBase):
    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def StartDate(self, graph):
        return Date(2008, 1, 1)

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def EndDate(self, graph):
        return graph("Database", "PricingDate") + RDate("-0b")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def VaRStartDate(self, graph):
        return graph(self, "VaREndDate") + RDate("-5y-0b")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def VaREndDate(self, graph):
        return graph(self, "EndDate")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def BetaStartDate(self, graph):
        return graph(self, "VaRStartDate")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def BetaEndDate(self, graph):
        return graph(self, "EndDate")


# -----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import GetVal
    from agora.corelibs.unittest_utils import AddIfMissing
    from agora.system.ufo_shadow_book import ShadowBook
    import agora.system.ufo_database as ufo_database
    import agora.system.ufo_trade as ufo_trade

    AddIfMissing(Risk(Name="Risk"))

    ufo_database.prepare_for_test()
    trades = ufo_trade.prepare_for_test()

    book = AddIfMissing(ShadowBook(Name="TestBook", Denominated="GBP"))

    for trade in trades:
        book.Children += GetVal(trade, "Leaves")

    return [book]

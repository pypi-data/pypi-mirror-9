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

from onyx.core import (Curve, CurveIntersect, UfoBase, ReferenceField,
                       GetVal, GraphNodeVt)

__all__ = []

###############################################################################
class EquityPair(UfoBase):
    """
    class used to represent a pair of two equities.
    """
    Symbol1 = ReferenceField(obj_type="EquityAsset")
    Symbol2 = ReferenceField(obj_type="EquityAsset")

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        sym1 = GetVal(self.Symbol1, "Symbol")
        sym2 = GetVal(self.Symbol2, "Symbol")
        exchg_code1 = GetVal(GetVal(self.Symbol1, "Exchange"), "Code")
        exchg_code2 = GetVal(GetVal(self.Symbol2, "Exchange"), "Code")

        self.Name = "PAIR {0:s} {1:s} - " \
                    "{2:s} {3:s}".format(sym1, exchg_code1, sym2, exchg_code2)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Ratio(self, graph, start, end):
        """
        Ratio = Symbol1 / Symbol2
        """
        num = graph(self, "Symbol1")
        den = graph(self, "Symbol2")
        ccy_num = graph(num, "Denominated")
        ccy_den = graph(den, "Denominated")

        num_crv = graph(num, "GetCurve", start, end, "Close")
        den_crv = graph(den, "GetCurve", start, end, "Close")

        if ccy_num != ccy_den:
            # --- convert both to US$
            num_cross = "{0:3s}/USD".format(num_ccy)
            den_cross = "{0:3s}/USD".format(den_ccy)
            num_cross_crv = graph(num_cross, "GetCurve", start, end)
            den_cross_crv = graph(den_cross, "GetCurve", start, end)

            num_crv, den_crv, num_cross_crv, den_cross_crv = CurveIntersect([
                num_crv, den_crv, num_cross_crv, den_cross_crv])

            num_crv *= num_cross_crv
            den_crv *= den_cross_crv

        else:
            num_crv, den_crv = CurveIntersect([num_crv, den_crv])

        return Curve(num_crv.dates, num_crv.values / den_crv.values)


##-----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import Curve, SetDiddle

    from agora.corelibs.unittest_utils import AddIfMissing
    from agora.system.ufo_equity_asset import EquityAsset

    import agora.system.ufo_currency as ufo_currency
    import agora.system.ufo_database as ufo_database
    import agora.system.ufo_holiday_calendar as ufo_holiday_calendar
    import agora.system.ufo_exchange as ufo_exchange

    ufo_database.prepare_for_test()
    ufo_holiday_calendar.prepare_for_test()
    ufo_currency.prepare_for_test()
    ufo_exchange.prepare_for_test()


    sse_info = {
        "Symbol": "SSE",
        "Exchange": "London",
        "Tickers": {
            "Bloomberg": "SSE",
        },
        "Multiplier": 0.01,
    }

    cna_info = {
        "Symbol": "CNA",
        "Exchange": "London",
        "Tickers": {
            "Bloomberg": "CNA",
        },
        "Multiplier": 0.01,
    }

    AddIfMissing(EquityAsset(**sse_info))
    AddIfMissing(EquityAsset(**cna_info))
    AddIfMissing(EquityPair(Symbol1="EQ SSE LN", Symbol2="EQ CNA LN"))

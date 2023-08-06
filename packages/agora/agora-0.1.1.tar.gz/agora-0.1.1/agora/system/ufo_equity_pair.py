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

from agora.econometrics.regression import RobustRegression

import numpy as np

__all__ = []


###############################################################################
class EquityPair(UfoBase):
    """
    class used to represent a pair of two equities.
    """
    Symbol1 = ReferenceField(obj_type="EquityAsset")
    Symbol2 = ReferenceField(obj_type="EquityAsset")

    name_fmt = "EQP {0:s} {1:s} - {2:s} {3:s}"

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        sym1 = GetVal(self.Symbol1, "Symbol")
        sym2 = GetVal(self.Symbol2, "Symbol")
        exchg_code1 = GetVal(GetVal(self.Symbol1, "Exchange"), "Code")
        exchg_code2 = GetVal(GetVal(self.Symbol2, "Exchange"), "Code")

        self.Name = self.name_fmt.format(sym1, exchg_code1, sym2, exchg_code2)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Curves(self, graph, start, end):
        sym1 = graph(self, "Symbol1")
        sym2 = graph(self, "Symbol2")
        ccy1 = graph(sym1, "Denominated")
        ccy2 = graph(sym2, "Denominated")

        sym1_crv = graph(sym1, "GetCurve", start, end, "Close")
        sym2_crv = graph(sym2, "GetCurve", start, end, "Close")

        if ccy1 != ccy2:
            # --- convert both to US$
            cross1 = "{0:3s}/USD".format(ccy1)
            cross2 = "{0:3s}/USD".format(ccy2)
            cross1_crv = graph(cross1, "GetCurve", start, end)
            cross2_crv = graph(cross2, "GetCurve", start, end)

            sym1_crv, sym2_crv, cross1_crv, cross2_crv = CurveIntersect([
                sym1_crv, sym2_crv, cross1_crv, cross2_crv])

            sym1_crv *= cross1_crv
            sym2_crv *= cross2_crv

            return sym1_crv, sym2_crv
        else:
            return CurveIntersect([sym1_crv, sym2_crv])

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Ratio(self, graph, start, end, use_log=False):
        """
        Description:
            Ratio is defined as:
                Ratio = Symbol1 / Symbol2
            or, if use_log is True:
                Ratio = log(Symbol1 / Symbol2)
        """
        num_crv, den_crv = graph(self, "Curves", start, end)

        if use_log:
            return Curve(num_crv.dates,
                         np.log(num_crv.values / den_crv.values))
        else:
            return Curve(num_crv.dates, num_crv.values / den_crv.values)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Spread(self, graph, start, end, reg_range=None):
        """
        Description:
            Spread is defined as:
                Spread = log(Symbol1) - beta*log(Symbol2) - alpha
        """
        sym1_crv, sym2_crv = graph(self, "Curves", start, end)

        if reg_range is None:
            m, c, _, spread = RobustRegression(np.log(sym2_crv.values),
                                               np.log(sym1_crv.values))
        else:
            x = sym2_crv.values[-reg_range:]
            y = sym1_crv.values[-reg_range:]
            m, c, _, _ = RobustRegression(np.log(x), np.log(y))

        return Curve(sym1_crv.dates, spread)


##-----------------------------------------------------------------------------
def prepare_for_test():
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

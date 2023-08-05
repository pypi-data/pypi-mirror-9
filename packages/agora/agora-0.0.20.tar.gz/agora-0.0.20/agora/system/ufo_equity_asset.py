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

from onyx.core import (Date, Curve, Knot, CalcTerm, Interpolate,
                       Transaction, DelObj, GetVal, TsDbQuery, TsDbGetCurve,
                       StringField, DictField, ReferenceField, GraphNodeVt)

from agora.system.ufo_asset import Asset
from agora.corelibs.ufo_functions import RetainedFactory
from agora.corelibs.date_functions import DateOffset

import numpy as np
import math

__all__ = ["EquityAsset"]

CRV_CHOICES = {
    "Adjusted": "GetCurve",
    "Marks": "GetMarks",
    "Dividends": "GetDividends",
}


###############################################################################
class EquityAsset(Asset):
    """
    class used to represent an equity asset and to provide access to its
    curve of historical prices and price fixes.
    """
    Tickers = DictField()
    Isin = StringField()
    Sedol = StringField()
    Country = ReferenceField(obj_type="Category")
    Region = ReferenceField(obj_type="Category")
    Sector = ReferenceField(obj_type="Category")
    Subsector = ReferenceField(obj_type="Category")
    TimeSeries = StringField()
    Marks = StringField()
    Dividends = StringField()

    name_fmt = "EQ {0:s} {1:s}"

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        super().__post_init__()

        exchange_code = GetVal(self.Exchange, "Code")

        self.Name = self.name_fmt.format(self.Symbol, exchange_code)
        self.Country = self.Country or GetVal(self.Exchange, "Country")
        self.Region = self.Region or GetVal(self.Exchange, "Region")

        # --- name of the time-series that store historical adjusted prices,
        #     historical closes (marks) and dividends
        fields = self.Symbol, exchange_code
        self.TimeSeries = "EQ-TS {0:s} {1:s}".format(*fields)
        self.Marks = "EQ-MKS {0:s} {1:s}".format(*fields)
        self.Dividends = "EQ-DIV {0:s} {1:s}".format(*fields)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Ticker(self, graph, platform="Bloomberg"):
        """
        If ticker for a given platform is missing, it's understood that we
        should default to the one for Bloomberg.
        """
        try:
            return graph(self, "Tickers")[platform]
        except KeyError:
            return graph(self, "Tickers")["Bloomberg"]

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def GetDividends(self, graph, start=None, end=None):
        return graph(graph(self, "Dividends"), "PrcFixCurve", start, end)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Spot(self, graph):
        """
        Return the official close value as of MktDataDate (or the most recent
        close if ForceStrict is False) in the Denominated currency.
        """
        return graph(graph(self, "Marks"), "Price")*graph(self, "Multiplier")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Last(self, graph):
        """
        Return the knot with the most recent close value irrespective of
        MktDataDate in the Denominated currency.
        """
        marks = graph(self, "Marks")
        date = graph(marks, "LastBefore")
        value = graph(marks, "PrcByDate", date, strict=True)
        return Knot(date, value*graph(self, "Multiplier"))

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def GetCurve(self, graph, start=None, end=None, field=None):
        name = graph(self, "TimeSeries")
        return TsDbGetCurve(name, start, end, "HLOCV", field)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def GetMarks(self, graph, start=None, end=None):
        return graph(graph(self, "Marks"), "PrcFixCurve", start, end)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def DividendForecast(self, graph):
        """
        Include dividends paid within the last 12 months and pick the most
        recent as forcasted value.
        """
        mdd = graph("Database", "MktDataDate")
        div = graph(self, "GetDividends").crop(DateOffset(mdd, "-12m"))
        val = Interpolate(div, mdd, method="InterpolateStep")

        rules = ["+1y-0b", "+2y-0b", "+3y-0b"]
        cal = graph(self, "HolidayCalendar")
        dts = [[DateOffset(d, r, cal) for r in rules] for d in div.dates]
        dts = {item for sublist in dts for item in sublist}
        vls = val*np.ones(len(dts))

        return Curve(dts, vls)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def DividendYield(self, graph, start, end):
        """
        DividendYield, calculated by including all dividends that are expected
        to be paid between start and end date and annualizing with continuous
        compounding.
        """
        if start <= end:
            return 0.0

        fcast = graph(self, "DividendForecast").crop_values(start, end)
        tot_dvd = fcast.sum()*graph(self, "Multiplier")
        spot = graph(self, "Spot")

        return math.log(tot_dvd/spot + 1.0) / CalcTerm(start, end)

    ##-------------------------------------------------------------------------
    ##  Auxiliary VTs used by the edit screen

    @RetainedFactory(default="Adjusted")
    def Selection(self, graph):
        pass

    @GraphNodeVt()
    def DisplayCurve(self, graph):
        return graph(self, CRV_CHOICES[graph(self, "Selection")])

    ##-------------------------------------------------------------------------
    def delete(self):
        # --- delete timeseries
        TsDbQuery("DELETE FROM HlocvCurves WHERE "
                  "Name = %s", parms=(self.TimeSeries,))

        # --- delete price fixes
        with Transaction("cleanup"):
            DelObj(self.Marks)
            DelObj(self.Dividends)


##-----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.unittest_utils import AddIfMissing
    from agora.system.ufo_price_fix import PriceFix

    import agora.system.ufo_currency as ufo_currency
    import agora.system.ufo_database as ufo_database
    import agora.system.ufo_holiday_calendar as ufo_holiday_calendar
    import agora.system.ufo_exchange as ufo_exchange
    import agora.system.ufo_price_fix as ufo_price_fix

    ufo_database.prepare_for_test()
    ufo_holiday_calendar.prepare_for_test()
    ufo_currency.prepare_for_test()
    ufo_exchange.prepare_for_test()
    ufo_price_fix.prepare_for_test()

    ibm_info = {
        "Symbol": "IBM",
        "Exchange": "NYSE",
        "Tickers": {"Bloomberg": "IBM"},
        "Multiplier": 1.00,
    }

    AddIfMissing(EquityAsset(**ibm_info))
    prc_fix = AddIfMissing(PriceFix(Name=GetVal("EQ IBM US", "Marks")))
    prc_fix.add_dated("Price", Date.today(), 100.0)

    ng_info = {
        "Symbol": "NG/",
        "Exchange": "London",
        "Tickers": {
            "Bloomberg": "NG/",
            "Google": "NG",
            "Yahoo": "NG",
            "WSJ": "NG."
        },
        "Multiplier": 0.01,
    }

    AddIfMissing(EquityAsset(**ng_info))
    prc_fix = AddIfMissing(PriceFix(Name=GetVal("EQ NG/ LN", "Marks")))
    prc_fix.add_dated("Price", Date.today(), 900.0)

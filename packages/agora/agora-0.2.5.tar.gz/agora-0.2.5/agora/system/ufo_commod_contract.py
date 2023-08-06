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

from.onyx.core import (LYY2Date, Knot,
                       UfoBase, DelObj, UpdateObj, Transaction,
                       GetVal, SetVal, TsDbGetCurve, TsDbQuery,
                       GraphNodeVt, StringField, ReferenceField)

from agora.corelibs.date_functions import DateOffset
from agora.corelibs.ufo_functions import InheritAsProperty
from.agora.system.ufo_asset import Asset

__all__ = ["CommodCnt"]

REPLACE = Asset._json_fields + ["Market", "CntType"]


###############################################################################
@InheritAsProperty(REPLACE, "CommodAsset")
class CommodCnt(Asset):
    """
    This class used to access commod contract information and the relative
    timeseries.
    """
    # --- this is the parent object that babysits all contracts on the same
    #     commodity
    CommodAsset = ReferenceField(obj_type="CommodAsset")

    # --- DeliveryMonth is the LYY code for the contract
    DeliveryMonth = StringField()
    Marks = StringField()
    TimeSeries = StringField()

    # -------------------------------------------------------------------------
    def __post_init__(self):
        mkt = GetVal(self.CommodAsset, "Market")
        sym = GetVal(self.CommodAsset, "Symbol")
        args = mkt, sym, self.DeliveryMonth

        self.Name = self.get_name(*args)
        self.Marks = "CNT-MKS {0:s} {1:s} {2:3s}".format(*args)
        self.TimeSeries = "CNT-TS {0:s} {1:s} {2:3s}".format(*args)

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def FutSettDate(self, graph):
        rule = graph(graph(self, "CommodAsset"), "SettDateRule")
        cal = graph(graph(self, "CommodAsset"), "HolidayCalendar")
        mth = graph(self, "DeliveryMonth")
        return DateOffset(LYY2Date(mth), rule, cal)

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def VolEndDate(self, graph):
        return graph(self, "FutSettDate")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def OptExpDate(self, graph):
        rule = graph(graph(self, "CommodAsset"), "OptExpDateRule")
        cal = graph(graph(self, "CommodAsset"), "HolidayCalendar")
        return DateOffset(graph(self, "FutSettDate"), rule, cal)

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Spot(self, graph):
        """
        Return the official close value as of MktDataDate (or the most recent
        close if ForceStrict is False) in the Denominated currency.
        """
        prc = graph(graph(self, "Marks"), "Price")
        return prc*graph(self, "Multiplier")

    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def GetCurve(self, graph, start=None, end=None, field=None):
        name = graph(self, "TimeSeries")
        if graph(self, "CntType") == "HLOCV":
            return TsDbGetCurve(name, start, end, "HLOCV", field)
        else:
            return TsDbGetCurve(name, start, end, "CRV", field)

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def GetMarks(self, graph, start=None, end=None):
        return graph(graph(self, "Marks"), "PrcFixCurve", start, end)

    # -------------------------------------------------------------------------
    def delete(self):
        # --- delete time-series from TsDb
        if GetVal(self, "CntType") == "HLOCV":
            query = "DELETE FROM HLOCVCurves WHERE Name = %s"
        else:
            query = "DELETE FROM Curves WHERE Name = %s"

        # --- delete timeseries
        TsDbQuery(query, parms=(self.TimeSeries,))

        # --- delete price fixes
        with Transaction("cleanup"):
            DelObj(self.Marks)

        # --- remove from set of contracts for the CommodAsset object
        cnts = GetVal(self.CommodAsset, "Contracts")
        cnts.remove(self.DeliveryMonth)

        SetVal(self.CommodAsset, "Contracts", cnts)
        UpdateObj(self.CommodAsset)

    # -------------------------------------------------------------------------
    @classmethod
    def get_name(cls, symbol, market, del_mth):
        """
        Generate contract's name from Market, Symbol, and DeliveryMonth
        """
        return "CNT {0:s} {1:s} {2:3s}".format(symbol, market, del_mth)

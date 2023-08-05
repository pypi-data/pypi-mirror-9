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

__all__ = ["CommodCnt"]


###############################################################################
class CommodCnt(UfoBase):
    """
    class used to access COMMOD Contract information and the relative
    timeseries.
    """
    Asset = ReferenceField(obj_type="CommodAsset")
    # --- DeliveryMonth is the LYY code for the contract
    DeliveryMonth = StringField()
    Marks = StringField()
    TimeSeries = StringField()

    # --- string format for contract's name from Market, Symbol, DeliveryMonth
    cnt_fmt = "CNT {0:s} {1:s} {2:3s}"

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        mkt = GetVal(self.Asset, "Market")
        sym = GetVal(self.Asset, "Symbol")
        args = mkt, sym, self.DeliveryMonth

        self.Name = self.cnt_fmt.format(*args)
        self.Marks = "CNT-MKS {0:s} {1:s} {2:3s}".format(*args)
        self.TimeSeries = "CNT-TS {0:s} {1:s} {2:3s}".format(*args)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Market(self, graph):
        # --- Market is inherited from that of the underlying Asset
        return graph(graph(self, "Asset"), "Market")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Symbol(self, graph):
        # --- Symbol is inherited from that of the underlying Asset
        return graph(graph(self, "Asset"), "Symbol")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def CntType(self, graph):
        # --- CntType is inherited from that of the underlying Asset
        return graph(graph(self, "Asset"), "CntType")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def FutSettDate(self, graph):
        rule = graph(graph(self, "Asset"), "SettDateRule")
        cal = graph(graph(self, "Asset"), "HolidayCalendar")
        mth = graph(self, "DeliveryMonth")
        return DateOffset(LYY2Date(mth), rule, cal)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def VolEndDate(self, graph):
        return graph(self, "FutSettDate")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def OptExpDate(self, graph):
        rule = graph(graph(self, "Asset"), "OptExpDateRule")
        cal = graph(graph(self, "Asset"), "HolidayCalendar")
        return DateOffset(graph(self, "FutSettDate"), rule, cal)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Spot(self, graph):
        """
        Return the official close value as of MktDataDate (or the most recent
        close if ForceStrict is False) in the Denominated currency.
        """
        prc = graph(graph(self, "Marks"), "Price")
        return prc*graph(graph(self, "Asset"), "Multiplier")

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
        return Knot(date, value*graph(graph(self, "Asset"), "Multiplier"))

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def GetCurve(self, graph, start=None, end=None, field=None):
        name = graph(self, "TimeSeries")
        if graph(self, "CntType") == "HLOCV":
            return TsDbGetCurve(name, start, end, "HLOCV", field)
        else:
            return TsDbGetCurve(name, start, end, "CRV", field)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def GetMarks(self, graph, start=None, end=None):
        return graph(graph(self, "Marks"), "PrcFixCurve", start, end)

    ##-------------------------------------------------------------------------
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

        # --- remove from set of contracts for the Asset object
        cnts = GetVal(self.Asset, "Contracts")
        cnts.remove(self.DeliveryMonth)

        SetVal(self.Asset, "Contracts", cnts)
        UpdateObj(self.Asset)

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

from onyx.core import (CurveIntersect, DateRange, Date2LYY, LYY2Date,
                       CountBizDays, Date, Curve,
                       AddObj, GetObj, DelObj, ObjNotFound, Transaction,
                       TsNotFound, GraphNodeVt,
                       StringField, SelectField, IntField, SetField)

from agora.corelibs.date_functions import DateOffset
from.agora.system.ufo_asset import Asset
from agora.system.ufo_commod_contract import CommodCnt

import numpy as np
import collections
import relativedelta

__all__ = ["CommodAsset"]

VALID_UNITS = ["BBL", "MT", "MWh", "Therm", "Day"]


###############################################################################
class CommodAsset(Asset):
    """
    class used to represent commodity assets and to get access to their
    contracts and forward curve.
    """
    Market = StringField()
    Units = SelectField(options=VALID_UNITS)
    # --- SettDateRule is used to determine the futures settlement date of a
    #     futures contract from its LYY code as follows:
    #         FutSettDate = DateOffset(LYY2Date(DeliveryMonth), SettDateRule)
    SettDateRule = StringField(default="+e")
    # --- OptExpDateRule is used to determine the options expiration date
    #     starting from the settlement date of the futures contract.
    OptExpDateRule = StringField(default="+e")
    CntType = SelectField(options=["CLOSE", "HLOCV"])
    NrbyOffset = IntField()
    Contracts = SetField(default=set())

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        # --- always call base class __post_init__
        super().__post_init__()
        self.Name = "COMMOD {0:s} {1:s}".format(self.Market, self.Symbol)

        # --- calculate the neraby offset based on the settlement date rule and
        #     an arbitrary reference date
        ref = DateOffset(Date.today(), "+0J")
        di = DateOffset(ref, self.SettDateRule, self.HolidayCalendar)
        df = DateOffset(ref, "+e", self.HolidayCalendar)

        self.NrbyOffset = relativedelta.relativedelta(df, di).months
        if self.NrbyOffset < 0:
            raise RuntimeError("Negative NrbyOffset?!? Check SettDateRule.")

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def GetContract(self, graph, delmth):
        """
        Description:
            Return the COMMOD CONTRACT object for a specific delivery month.
        Inputs:
            delmth - the delivery month in LYY format (as in Z11)
        Returns:
            A string.
        """
        if delmth in graph(self, "Contracts"):
            market = graph(self, "Market")
            symbol = graph(self, "Symbol")
            return CommodCnt.cnt_fmt.format(market, symbol, delmth)
        else:
            raise NameError("Contract {0:s} not found in the set of "
                            "Contracts of {1:s}".format(delmth, self.Name))

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def ActiveByDate(self, graph, date):
        """
        Return the active contract (first nearby) as of a given date.
        """
        cal = graph(self, "HolidayCalendar")
        sdr = graph(self, "SettDateRule")

        rule = "+{0:d}m+0J".format(graph(self, "NrbyOffset"))
        cnt_dt = DateOffset(date, rule)

        if date > DateOffset(cnt_dt, sdr, cal):
            cnt_dt = DateOffset(cnt_dt, "+1m")

        return Date2LYY(cnt_dt)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def GetStrip(self, graph, start, end, avg_type="LAST"):
        """
        Description:
            Return the historical timeseries for the required strip. The strip
            is defined as the average of all contracts with delivery date
            within start and end dates.
        Inputs:
            start    - the start date defining the strip
            end      - the   end date defining the strip
            avg_type - the averaging type. Valid choices are:
                        - DAILYCALDAYS
                        - DAILYBIZDAYS
                        - LAST
        Example:
            GetStrip(Date(2012, 1, 1), Date(2012, 12, 31), "DAILYBIZDAYS")
            returns the historical curve for the Cal12 swap for a commodity
            that prices out every business day.
        """
        cal = graph(self, "HolidayCalendar")
        sdr = graph(self, "SettDateRule")
        nbo = graph(self, "NrbyOffset")

        avg_type = avg_type.upper()
        if avg_type == "DAILYCALDAYS":
            sd_rule = "+0d"
            ed_rule = "-0d"
            inc_rule = "+1d"
        elif avg_type == "DAILYBIZDAYS":
            sd_rule = "+0b"
            ed_rule = "-0b"
            inc_rule = "+1b"
        elif avg_type == "LAST":
            sd_rule = "+0J{0:s}".format(sdr)
            ed_rule = "+0J{0:s}".format(sdr)
            inc_rule = "+{0:d}m+0J{1:s}".format(1+nbo, sdr)
        else:
            raise NameError("Unrecognized "
                            "averaging type {0:s}".format(avg_type))

        sd = DateOffset(start, sd_rule, cal)
        ed = DateOffset(end, ed_rule, cal)
        cnts = [graph(self, "ActiveByDate", d)
                for d in DateRange(sd, ed, inc_rule, cal)]

        # --- accumulate historical prices and quantities for all relevant
        #     contracts
        crvs = []
        qtys = []
        for cnt, qty in collections.Counter(cnts).items():
            cnt = graph(self, "GetContract", cnt)
            crvs.append(graph(cnt, "GetCurve", field="Close"))
            qtys.append(float(qty))

        crvs = CurveIntersect(crvs)
        qtot = qtys[0]
        svls = qtys[0]*crvs[0].values  # sum of values (element by element)
        for k in range(1, len(crvs)):
            qtot += qtys[k]
            svls += qtys[k]*crvs[k].values

        return Curve(crvs[0].dates, svls/qtot)

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def FwdCurve(self, graph):
        """
        Description:
            Return the forward curve as of a given date.
        Returns:
            A curve.
        """
        mdd = graph("Database", "MktDataDate")
        cal = graph(self, "HolidayCalendar")
        if mdd <= DateOffset(mdd, graph(self, "SettDateRule"), cal):
            offset = graph(self, "NrbyOffset")
        else:
            offset = 1 + graph(self, "NrbyOffset")

        sd = DateOffset(mdd, "+{0:d}m+0J".format(offset), cal)

        fwd_crv = Curve()
        for del_mth in graph(self, "Contracts"):
            # --- contract's month start date
            cnt_sd = LYY2Date(del_mth)
            # --- only include contracts in the range
            if sd <= cnt_sd:
                cnt = graph(self, "GetContract", del_mth)
                try:
                    fwd_crv[cnt_sd] = graph(cnt, "Spot")
                except TsNotFound:
                    # --- no time series for this contract: skip
                    continue

        return fwd_crv

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Nearby(self, graph, idx=0, start=None, end=None, smooth=False):
        """
        Description:
            Returns the historical time series for a given nearby month.
        Inputs:
            idx    - the nearby index (0 is prompt month)
            start  - the start date of the curve
            end    - the   end date of the curve
            smooth - if True, use a weighted combination of two consecutive
                     months
        """
        if idx < 0:
            raise ValueError("Nearby index cannot "
                             "be negative: idx = {0:d}".format(idx))

        # --- if available, use default values for sd and ed
        start = start or Date.low_date()
        end = end or graph("Database", "MktDataDate")
        cal = graph(self, "HolidayCalendar")

        # --- date rules that define the portion of the curve to be used for
        #     each contract
        rule_sd = "-1m{0:s}+1d".format(graph(self, "SettDateRule"))
        rule_ed = graph(self, "SettDateRule")

        # --- for all contracts in the range, select the ones that have a
        #     non-empty time series within the required date range
        cnts_iter = (Date2LYY(d) for d in DateRange(start, end, "0J+1m", cal))
        cnts_within_range = [cnt for cnt in cnts_iter
                             if cnt in graph(self, "Contracts")]

        # --- get start dates for the first and last contracts in the range
        first_cnt_sd = LYY2Date(cnts_within_range[0])
        last_cnt_sd = LYY2Date(cnts_within_range[-1])
        last_cnt_sd = DateOffset(last_cnt_sd,
                                 "{0:d}m+0J".format(graph(self, "NrbyOffset")))

        dts = []
        vls = []
        if smooth:
            # --- use a weighted combination of two consecutive months. weights
            #     are scaled linearly.
            rule0 = "{0:d}m+0J".format(idx)
            rule1 = "{0:d}m+0J".format(1+idx)
            for d in DateRange(first_cnt_sd, last_cnt_sd, "+1m", cal):
                mth0 = DateOffset(d, rule0, cal)
                mth1 = DateOffset(d, rule1, cal)
                csd = DateOffset(d, rule_sd, cal)
                ced = DateOffset(d, rule_ed, cal)
                try:
                    cnt0 = graph(self, "GetContract", Date2LYY(mth0))
                    cnt1 = graph(self, "GetContract", Date2LYY(mth1))
                    crv0 = graph(cnt0, "GetCurve", csd, ced, field="Close")
                    crv1 = graph(cnt1, "GetCurve", csd, ced, field="Close")
                except TsNotFound:
                    continue

                m = CountBizDays(csd, ced, cal)
                n = len(crv0)

                if n != m or n != len(crv1):
                    continue

                w = (np.cumsum(np.ones(n)) - 1) / (n - 1)
                mix = (1.0 - w)*crv0.values + w*crv1.values

                dts += crv0.dates
                vls += mix.tolist()
        else:
            rule = "{0:d}m+0J".format(idx)
            for d in DateRange(first_cnt_sd, last_cnt_sd, "+1m", cal):
                mth = DateOffset(d, rule, cal)
                csd = DateOffset(d, rule_sd, cal)
                ced = DateOffset(d, rule_ed, cal)
                try:
                    cnt = graph(self, "GetContract", Date2LYY(mth))
                    crv = graph(cnt, "GetCurve", csd, ced, field="Close")
                    dts += crv.dates
                    vls += crv.values.tolist()
                except TsNotFound:
                    continue

        return Curve(dts, vls).crop(start, end)

    ###########################################################################
    ##  Returns the historical values for a given rolling strip
    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def RollingStrip(self, graph, strip="Quarter",
                     idx=1, start=None, end=None, avg_type="LAST"):
        """
        Description:
            Return the historical time series for a given rolling strip.
        Inputs:
            strip    - choose among "Qrater", "Calendar"
            idx      - the nearby index (0 is prompt strip)
            start    - the start date of the curve
            end      - the end date of the curve
            avg_type - the averaging type (see GetStrip).
        Returns:
            A Curve.
        """
        if idx < 0:
            raise ValueError("Nearby index cannot "
                             "be negative: idx = {0:d}".format(idx))

        # --- if available, use default values for sd and ed
        start = start or Date.low_date()
        end = end or graph("Database", "MktDataDate")
        cal = graph(self, "HolidayCalendar")

        # --- date rules that define the portion of the curve to be used for
        #     each contract
        rule_sd = "-1m{0:s}+1d".format(graph(self, "SettDateRule"))
        rule_ed = graph(self, "SettDateRule")

        if strip == "Quarter":
            rule_i = "+{0:d}m+q".format(3*idx)
            rule_f = "+{0:d}m+Q".format(3*idx)
        elif strip == "Calendar":
            rule_i = "+{0:d}y+A".format(idx)
            rule_f = "+{0:d}y+E".format(idx)
        else:
            raise RuntimeError("Unrecognized strip type {0:s}".format(strip))

        # --- for all contracts in the range, select the ones that have a
        #     non-empty time series within the required date range
        cnts_iter = (Date2LYY(d) for d in DateRange(start, end, "0J+1m", cal))
        cnts_within_range = [cnt for cnt in cnts_iter
                             if cnt in graph(self, "Contracts")]

        # --- get start dates for the first and last contracts in the range
        first_cnt_sd = LYY2Date(cnts_within_range[0])
        last_cnt_sd = LYY2Date(cnts_within_range[-1])
        last_cnt_sd = DateOffset(last_cnt_sd,
                                 "{0:d}m+0J".format(graph(self, "NrbyOffset")))

        dts = []
        vls = []
        for d in DateRange(first_cnt_sd, last_cnt_sd, "+1m", cal):
            di = DateOffset(d, rule_i, cal)
            df = DateOffset(d, rule_f, cal)
            crv = graph(self, "GetStrip", di, df, avg_type)
            crv = crv.corp(DateOffset(d, rule_sd, cal),
                           DateOffset(d, rule_ed, cal))
            dts += crv.dates
            vls += crv.values.tolist()

        return Curve(dts, vls).crop(start, end)

    ##-------------------------------------------------------------------------
    def create_contracts(self, contracts):
        mkt = self.Market
        sym = self.Symbol
        for cnt in contracts:
            if not cnt in self.Contracts:
                cnt_name = CommodCnt.cnt_fmt.format(mkt, sym, cnt)
                try:
                    cnt_obj = GetObj(cnt_name)
                    if cnt_obj.Asset == self.Name:
                        self.Contracts.add(cnt)
                    else:
                        raise ObjNotFound()
                except ObjNotFound:
                    # --- contract wasn't found: create a new one
                    AddObj(CommodCnt(self.Name, cnt))
                    self.Contracts.add(cnt)

    ##-------------------------------------------------------------------------
    def delete(self):
        with Transaction("deleting contracts"):
            mkt = self.Market
            sym = self.Symbol
            # --- conversion to tuple is needed because the delete method of a
            #     contract removes such contract from the set of contracts of
            #     the asset.
            for cnt in tuple(self.Contracts):
                cnt_name = CommodCnt.cnt_fmt.format(mkt, sym, cnt)
                try:
                    DelObj(cnt_name)
                except ObjNotFound():
                    pass

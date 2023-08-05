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

from onyx.core import (Structure, CurveIntersect,
                       GraphNodeVt, ChildrenIterator, EvalBloc, SetDiddle)

from agora.risk.timeseries_functions import prices_for_risk

import numpy as np
import matplotlib.mlab
import math

__all__ = ["pca_analysys", "risk_metrics", "worst_loss"]


##-----------------------------------------------------------------------------
def add_risk_value_types(cls):
    """
    Description:
        Class decorator. It can be applied to any class exposing the MktValUSD
        Value Type.
        It adds the following Value Types to the decorated class:
            Deltas
            GrossExposure
            NetExposure
            RiskMetrics
        These are further auxiliary Value Types used by the ones described
        above:
            RiskMktValues
    """
    ##-------------------------------------------------------------------------
    def Deltas(self, graph):
        deltas = Structure()
        for kid in ChildrenIterator(self, "MktValUSD", "Spot"):
            spot = graph(kid, "Spot")
            shift = 0.01*spot
            with EvalBloc() as eb:
                SetDiddle(kid, "Spot", spot+shift, eb)
                up = graph(self, "MktValUSD")
                SetDiddle(kid, "Spot", spot-shift, eb)
                dw = graph(self, "MktValUSD")
            deltas[kid] = (up-dw) / (2.0*shift)
        return deltas

    ##-------------------------------------------------------------------------
    def GrossExposure(self, graph):
        gross = 0.0
        for sec, qty in graph(self, "Delta").items():
            try:
                spot_usd = graph(sec, "SpotForRisk")
            except AttributeError:
                # --- skip securities that don't expose SpotForRisk value type
                continue
            gross += math.fabs(qty)*spot_usd
        return gross

    ##-------------------------------------------------------------------------
    def NetExposure(self, graph):
        net = 0.0
        for sec, qty in graph(self, "Delta").items():
            try:
                spot_usd = graph(sec, "SpotForRisk")
            except AttributeError:
                # --- skip securities that don't expose SpotForRisk value type
                continue
            net += qty*spot_usd
        return net

    ##-------------------------------------------------------------------------
    def Betas(self, graph):
        start = graph("Risk", "BetaStartDate")
        end = graph("Risk", "BetaEndDate")
        betas = Structure()
        index_rets = graph("Risk", "IndexReturns", start, end)
        for kid in ChildrenIterator(self, "MktValUSD", "Spot"):
            # --- skip securities that don't expose PricesForRisk value type
            try:
                prcs = graph(kid, "PricesForRisk", start, end)
            except AttributeError:
                continue
            rets = np.diff(np.log(prcs.values))
            A = np.vstack([index_rets, np.ones_like(index_rets)]).T
            beta, alpha = np.linalg.lstsq(A, rets)[0]
            betas[kid] = beta
        return betas

    ##-------------------------------------------------------------------------
    def RiskMktValues(self, graph, start, end):
        mkt_vls = None
        for sec, qty in graph(self, "Delta").items():
            # --- skip securities that don't expose PricesForRisk value type
            try:
                prcs = graph(sec, "PricesForRisk", start, end)
            except AttributeError:
                continue
            if mkt_vls is None:
                mkt_vls = qty*prcs
            else:
                mkt_vls += qty*prcs
        return mkt_vls

    ##-------------------------------------------------------------------------
    def RiskMetrics(self, graph):
        start = graph("Risk", "StartDate")
        end = graph("Risk", "EndDate")
        mkt_values = graph(self, "RiskMktValues", start, end)
        mkt_values_risk = mkt_values.crop(start=graph("Risk", "VaRStartDate"))

        daily_95 = risk_metrics(mkt_values_risk, ndays=1, pctl=95.0)
        weekly_95 = risk_metrics(mkt_values_risk, ndays=5, pctl=95.0)
        monthly_95 = risk_metrics(mkt_values_risk, ndays=21, pctl=95.0)

        daily_99 = risk_metrics(mkt_values_risk, ndays=1, pctl=99.0)
        weekly_99 = risk_metrics(mkt_values_risk, ndays=5, pctl=99.0)
        monthly_99 = risk_metrics(mkt_values_risk, ndays=21, pctl=99.0)

        worst_day = worst_loss(mkt_values, ndays=1)
        worst_week = worst_loss(mkt_values, ndays=5)
        worst_month = worst_loss(mkt_values, ndays=21)

        return {
            "Daily - 95": daily_95,
            "Weekly - 95": weekly_95,
            "Monthly - 95": monthly_95,
            "Daily - 99": daily_99,
            "Weekly - 99": weekly_99,
            "Monthly - 99": monthly_99,
            "Worst Day": worst_day,
            "Worst Week": worst_week,
            "Worst Month": worst_month,
        }

    # --- whack value types into the decorated class
    cls.Deltas = GraphNodeVt("Property")(Deltas)
    cls.GrossExposure = GraphNodeVt("Property")(GrossExposure)
    cls.NetExposure = GraphNodeVt("Property")(NetExposure)
    cls.RiskMktValues = GraphNodeVt("Calc")(RiskMktValues)
    cls.RiskMetrics = GraphNodeVt("Property")(RiskMetrics)

    return cls


##-----------------------------------------------------------------------------
def pca_analysys(names, start, end, agg=None):
    """
    Description:
        Return PCA analisys on the covariance matrix of the log-returns (based
        on close prices) of a set of securities.
    Inputs:
        names - a list of asset's names
        start - the start date
        end   - the end date
        agg   - an optional aggregation function (such as Weekly, etc)
    Returns:
        An instance of matplotlib.mlab.PCA
    """
    curves = [prices_for_risk(name, start, end) for name in names]
    curves = [crv for crv in curves if len(crv)]
    curves = CurveIntersect(curves)
    if agg is not None:
        curves = [agg(crv) for crv in curves]
    values = np.vstack([np.diff(np.log(crv.values)) for crv in curves]).T
    return matplotlib.mlab.PCA(values)


##-----------------------------------------------------------------------------
def risk_metrics(mkt_values, ndays=1, pctl=95.0):
    """
    Description:
        Return key risk metrics given daily timeseries of market values.
    Inputs:
        mkt_values - a curve with daily market values for the portfolio.
        ndays      - time-horizon for calculation of risk-metrics.
        pctl       - confidence level for calculation of VaR and cVaR.
    Returns:
        A dictionary with Std, VaR and cVaR keys.
    """
    if len(mkt_values) == 0:
        std = 0.0
        var = 0.0
        cvar = 0.0
    else:
        # --- flip the sign so that losses are positive numbers
        diffs = -(mkt_values.values[ndays:] - mkt_values.values[:-ndays])

        # --- for VaR and cVaR use non-overlapping differences
        pnl_loss = diffs[::ndays]
        pnl_loss -= pnl_loss.mean()

        std = pnl_loss.std()
        var = np.percentile(pnl_loss, pctl)
        cvar = pnl_loss[pnl_loss > var].mean()

    return {"Std": std,  "VaR": var, "cVaR": cvar}


##-----------------------------------------------------------------------------
def worst_loss(mkt_values, ndays=1):
    """
    Description:
        Return the wrost loss given daily timeseries of market values.
    Inputs:
        mkt_values - a curve with daily market values for the portfolio.
        ndays      - time-horizon for calculation of risk-metrics.
    Returns:
        A dictionary with MaxLoss and MaxLossDate keys.
    """
    if len(mkt_values) == 0:
        max_loss = 0.0
        max_loss_date = None
    else:
        # --- flip the sign so that losses are positive numbers
        diffs = -(mkt_values.values[ndays:] - mkt_values.values[:-ndays])

        # --- for max loss, consider all (i.e. overlapping) ndays-differences
        dates = mkt_values.dates[:-ndays]
        max_loss = diffs.max()

        max_loss_idx = matplotlib.mlab.find(diffs == max_loss)
        max_loss_date = dates[max_loss_idx].strftime("%d-%b-%Y")

    return {"MaxLoss": max_loss_idx, "MaxLossDate": max_loss_date}


if __name__ == "__main__":
    from onyx.core import Date, RDate, Weekly, GetVal
    from agora.corelibs.onyx_utils import OnyxInit

    ed = Date.today()
    sd = ed + RDate("-5y")

    sectors = ["Vertically Integrated", "IPP",
               "Renewables", "Regulated", "Energy"]

    countries = ["Italy", "Spain", "France", "Germany", "United Kingdom"]

    with OnyxInit():
        for sector in sectors:
            names = GetVal(sector, "Items")
            pca = pca_analysys(names, sd, ed, agg=Weekly)
            print("{0:>25s}: {1!s}".format(sector, pca.fracs[:4]))

        print()
        for country in countries:
            names = GetVal(country, "Items")
            pca = pca_analysys(names, sd, ed, agg=Weekly)
            print("{0:>25s}: {1!s}".format(country, pca.fracs[:4]))

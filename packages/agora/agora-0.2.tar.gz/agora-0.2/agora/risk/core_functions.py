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
                       GraphNodeVt, ChildrenSet, EvalBlock)

from agora.risk.timeseries_functions import prices_for_risk

import numpy as np
import matplotlib.mlab
import math

__all__ = [
    "WithRiskValueTypes",
    "pca_analysis",
    "risk_metrics",
    "worst_loss",
]


# -----------------------------------------------------------------------------
def WithRiskValueTypes(cls):
    """
    Description:
        Class decorator. It can be applied to any class implementing MktVal
        and MktValUSD Value Types.
        It adds the following Value Types to the decorated class:
            Deltas
            FxExposures
            GrossExposure
            NetExposure
            Betas
            VaR
            RiskMetrics
        These are further auxiliary Value Types used by the ones described
        above:
            RiskMktValues
    """
    # -------------------------------------------------------------------------
    def Deltas(self, graph):
        deltas = Structure()
        for kid in ChildrenSet(self, "MktValUSD", "Spot", "Asset"):
            cross = "{0:3s}/USD".format(graph(kid, "Denominated"))
            spot = graph(kid, "Spot")
            fx = graph(cross, "Spot")
            shift = 0.01*spot
            with EvalBlock() as eb:
                eb.set_diddle(kid, "Spot", spot+shift)
                up = graph(self, "MktValUSD")
                eb.set_diddle(kid, "Spot", spot-shift)
                dw = graph(self, "MktValUSD")
            deltas += Structure({kid: (up-dw) / (2.0*shift*fx)})
        deltas.drop_zeros()
        return deltas

    # -------------------------------------------------------------------------
    def FxExposures(self, graph):
        exposures = Structure()
        for kid in ChildrenSet(self, "MktVal", "Spot", "CurrencyCross"):
            spot = graph(kid, "Spot")
            shift = 0.01*spot
            with EvalBlock() as eb:
                eb.set_diddle(kid, "Spot", spot+shift)
                up = graph(self, "MktVal")
                eb.set_diddle(kid, "Spot", spot-shift)
                dw = graph(self, "MktVal")
            exposures += Structure({kid: (up-dw) / (2.0*shift)})
        exposures.drop_zeros()
        return exposures

    # -------------------------------------------------------------------------
    def GrossExposure(self, graph):
        gross = 0.0
        for sec, qty in graph(self, "Deltas").items():
            spot_usd = graph(sec, "SpotUSD")
            gross += math.fabs(qty)*spot_usd
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        fx = graph(cross, "Spot")
        return gross / fx

    # -------------------------------------------------------------------------
    def NetExposure(self, graph):
        net = 0.0
        for sec, qty in graph(self, "Deltas").items():
            spot_usd = graph(sec, "SpotUSD")
            net += qty*spot_usd
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        fx = graph(cross, "Spot")
        return net / fx

    # -------------------------------------------------------------------------
    def Betas(self, graph):
        start = graph("Risk", "BetaStartDate")
        end = graph("Risk", "BetaEndDate")
        betas = Structure()
        index_rets = graph("Risk", "IndexReturns", start, end)
        for kid in ChildrenSet(self, "MktValUSD", "Spot"):
            prcs = graph(kid, "PricesForRisk", start, end)
            rets = np.diff(np.log(prcs.values))
            A = np.vstack([index_rets, np.ones_like(index_rets)]).T
            beta, alpha = np.linalg.lstsq(A, rets)[0]
            betas[kid] = beta
        return betas

    # -------------------------------------------------------------------------
    def RiskMktValues(self, graph, start, end):
        # --- load fx to convert mkt_vls from USD to the Denominated
        #     currency
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        fx = graph(cross, "Spot")

        mkt_vls = None
        for sec, qty in graph(self, "Deltas").items():
            prcs = graph(sec, "PricesForRisk", start, end)
            if mkt_vls is None:
                mkt_vls = qty*prcs
            else:
                prcs, mkt_vls = CurveIntersect([prcs, mkt_vls])
                mkt_vls += qty*prcs

        return mkt_vls / fx

    # -------------------------------------------------------------------------
    def VaR(self, graph, ndays=1, pctl=95.0):
        start = graph("Risk", "StartDate")
        end = graph("Risk", "EndDate")

        mkt_values = graph(self, "RiskMktValues", start, end)
        mkt_values_risk = mkt_values.crop(start=graph("Risk", "VaRStartDate"),
                                          end=graph("Risk", "VaREndDate"))

        return risk_metrics(mkt_values_risk, ndays=ndays, pctl=pctl)

    # -------------------------------------------------------------------------
    def RiskMetrics(self, graph):
        start = graph("Risk", "StartDate")
        end = graph("Risk", "EndDate")

        mkt_values = graph(self, "RiskMktValues", start, end)
        mkt_values_risk = mkt_values.crop(start=graph("Risk", "VaRStartDate"),
                                          end=graph("Risk", "VaREndDate"))

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

    # --- here we whack value types into the decorated class
    cls.Deltas = GraphNodeVt("Property")(Deltas)
    cls.FxExposures = GraphNodeVt("Property")(FxExposures)
    cls.GrossExposure = GraphNodeVt("Property")(GrossExposure)
    cls.NetExposure = GraphNodeVt("Property")(NetExposure)
    cls.Betas = GraphNodeVt("Property")(Betas)
    cls.RiskMktValues = GraphNodeVt("Calc")(RiskMktValues)
    cls.VaR = GraphNodeVt("Calc")(VaR)
    cls.RiskMetrics = GraphNodeVt("Property")(RiskMetrics)

    return cls


# -----------------------------------------------------------------------------
def pca_analysis(names, start, end, agg=None):
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


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
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
    from onyx.core import GetVal
    from agora.corelibs.onyx_utils import OnyxInit
    import pprint
    with OnyxInit():
        for book in ("CARLO ISA", "CARLO SIPP", "LUIGI ISA", "PAOLO ISA"):
            print("\nBook:", book)
            print("positions:")
            pprint.pprint(GetVal(book, "Deltas"))
            print("Gross Exposure:", GetVal(book, "GrossExposure"))
            print("Net Exposure:", GetVal(book, "NetExposure"))
            print("Market Value", GetVal(book, "MktVal"))

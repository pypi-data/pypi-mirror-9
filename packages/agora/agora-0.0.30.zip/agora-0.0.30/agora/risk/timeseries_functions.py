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

from onyx.core import Curve, CurveIntersect, CurveUnion, GetVal

import numpy as np

__all__ = ["get_curve_usd", "prices_for_risk"]


##-----------------------------------------------------------------------------
def get_curve_usd(name, start, end):
    """
    Description:
        Given an asset, return the curve with close prices converted to USD.
    Inputs:
        name  - the asset's name
        start - the start date
        end   - the end date
    Returns:
        A Curve.
    """
    prc = GetVal(name, "GetCurve", start, end, field="Close")
    if len(prc) == 0:
        return Curve()

    cross = "{0:3s}/USD".format(GetVal(name, "Denominated"))
    fx = GetVal(cross, "GetCurve", start, end)
    prc, fx = CurveIntersect([prc, fx])
    return prc*fx


##-----------------------------------------------------------------------------
def merge_pirces(crv1, crv2):
    """
    Description:
        Merge two timeseries, from their log-return representation
    Inputs:
        crv1 - first curve, takes precedence
        crv2 - second curve, fills missing data in crv1
    Returns:
        A Curve.
    """
    # --- log-returns
    ret1 = Curve(crv1.dates[1:], np.log(crv1.values).diff())
    ret2 = Curve(crv1.dates[1:], np.log(crv2.values).diff())

    # --- combine returns, with priority to those from ret1
    ret = CurveUnion(ret1, ret2)

    # --- reconstruct series of prices from series of returns
    last = crv1.back.value
    rec = np.roll(last*np.exp(np.cumsum(-ret.values[::-1]))[::-1], -1)
    rec[-1] = last

    return Curve(ret.dates, rec)


##-----------------------------------------------------------------------------
def prices_for_risk(name, start, end):
    """
    Description:
        Return close prices converted to USD, sourcing them from a list of
        proxies when the time series for the security is too short.
    Inputs:
        name  - name of the EquityAsset object.
        start - start date
        end   - end date
    Returns:
        A Curve.
    """
    prcs = get_curve_usd(name, start, end)

    if prcs.back.date != end:
        raise RuntimeError("Missing prices at the end "
                           "of the curve for {0:s}".format(name))

    if prcs.front.date == start:
        return prcs

    for name_proxy in GetVal(name, "RiskProxies"):
        prcs_proxy = get_curve_usd(name_proxy, start, end)
        prcs = merge_pirces(prcs, prcs_proxy)

        if prcs.front.date == start:
            return prcs

    raise RuntimeError("Insufficient proxies for {0:s} "
                       "to be able to reconstruct the time series "
                       " for the range {1:s} - {2:s}".format(name, start, end))

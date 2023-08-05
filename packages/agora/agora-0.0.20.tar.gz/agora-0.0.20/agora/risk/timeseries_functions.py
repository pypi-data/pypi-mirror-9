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

from onyx.core import Curve, CurveUnion, GetVal

import numpy as np

__all__ = ["PricesForRisk"]


##-----------------------------------------------------------------------------
def merge_pirces(crv1, crv2):
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
def PricesForRisk(name, start, end):
    """
    Description:
        Return close prices sourcing them from a list of proxies if the
        time series for the requiredrequested security is too short.
    Inputs:
        name  - name of the EquityAsset object.
        start - start date
        end   - end date
    Returns:
        A Curve.
    """
    prcs = GetVal(name, "GetCurve", start, end, "Close")
    ccy = GetVal(name, "Denominated")

    if prcs.back.date != end:
        raise RuntimeError("Missing prices at the end "
                           "of the curve for {0:s}".format(name))

    if prcs.front.date == start:
        return prcs

    for name_proxy in GetVal(name, "RiskProxies"):
        prcs_proxy = GetVal(name_proxy, "GetCurve", start, end, "Close")
        ccy_proxy = GetVal(name_proxy, "Denominated")

        if ccy_proxy != ccy:
            cross = "{0:3s}/{1:3s}".format(ccy, ccy_proxy)
            fx = GetVal(cross, "GetCurve", start, end)
            prcs_proxy *= fx

        prcs = merge_pirces(prcs, prcs_proxy)

        if prcs.front.date == start:
            return prcs

    raise RuntimeError("Insufficient proxies for {0:s} "
                       "to be able to reconstruct the time series "
                       " for the range {1:s} - {2:s}".format(name, start, end))

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

from onyx.core import Curve, Knot, Date, RDate

import urllib.request

__all__ = ["fetch_oanda_hist"]

BASE_URL = ("http://www.oanda.com/convert/fxhistory?"
            "date_fmt=us&date={0:8s}&date1={1:8s}&"
            "exch={2:3s}&expr=USD&exch2={2:3s}&expr2=USD&"
            "format=CSV&redirected=1")

RD_START = RDate("+A")
RD_END = RDate("+E")
RD_INC = RDate("+1d")


##-----------------------------------------------------------------------------
def fetch_oanda_hist(ccy, start, end):
    """
    Description:
        Return historical prices for the ccy/USD cross (from www.oanda.com).
    Inputs:
        ccy   - the currency crossed agains USD (ccy/USD)
        start - the start date
        end   - the end date
    Returns:
        A Curve.
    """
    cross = Curve()
    sd = ed = start

    # --- retrives time series in batches of 1 calendar year
    while ed < end:
        ed = min(end, ed + RD_END)
        sd = max(start, ed + RD_START)

        url = BASE_URL.format(ed.strftime("%m/%d/%y"),
                              sd.strftime("%m/%d/%y"), ccy)
        html = urllib.request.urlopen(url).read().decode("utf-8")
        idx0 = html.find("Daily averages:")
        html = html[idx0:]
        idx0 = html.find("<PRE>") + 5
        idx1 = html.find("</PRE>") - 1
        html = html[idx0:idx1]

        if len(html):
            for row in html.split("\n"):
                knot = row.split(",")
                cross.append(Knot(Date.parse(knot[0], False), float(knot[1])))

        ed = ed + RD_INC

    return cross

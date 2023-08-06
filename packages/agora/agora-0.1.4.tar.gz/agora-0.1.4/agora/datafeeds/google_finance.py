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

import urllib.request
import json
import concurrent.futures

__all__ = ["fetch_google", "fetchmany_google"]

BASEURL = "http://finance.google.com/finance/info?client=ig&q={0:s}:{1:s}"
MAXTHREADS = 10


# -----------------------------------------------------------------------------
def to_float(prc):
    return None if prc == "" else float(prc.replace(",", ""))


# -----------------------------------------------------------------------------
def fetch_google(exchange, ticker, fields=["l"]):
    """
    Description:
        Fetch real-time or delayed data from Google Finance.
    Inputs:
        exchange - exchange symbol as defined by Google Finance
        ticker   - ticker symbol as defined by Google Finance
        fields   - the list of fields to be returned
    Returns:
        A list of values (same order as fields).
    """
    url = BASEURL.format(exchange, ticker)
    http = urllib.request.urlopen(url).read().decode("cp1252")
    data = json.loads(http[3:])[0]
    return [data[field] for field in fields]


# -----------------------------------------------------------------------------
def fetchmany_google(symbols, target=fetch_google):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAXTHREADS) as exe:
        data = list(exe.map(lambda s: target(*s), symbols))
    return data


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    from onyx.core import TableFilter
    from datafeeds_config import BBG_MAPPING
    import functools

    fetch = functools.partial(fetch_google, fields=["l", "cp_fix", "lt"])

    # --- remove rows that don't have a Google symbol set
    TableFilter(BBG_MAPPING, lambda row: row["Google"] is not None)

    # --- sort by bbg symbol
    BBG_MAPPING.sort(["Bloomberg"])

    data = fetchmany_google([tuple(row["Google"].split(":"))
                             for row in BBG_MAPPING], fetch)
    data = [(to_float(prc), to_float(chg), dt) for prc, chg, dt in data]

    for row in zip(BBG_MAPPING.column("Bloomberg"), data):
        print(row)

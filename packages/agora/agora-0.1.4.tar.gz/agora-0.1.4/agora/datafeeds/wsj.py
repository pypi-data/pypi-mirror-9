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
import concurrent.futures

BASEURL = 'http://quotes.wsj.com/{0:s}/{1:s}'
TAGTSAMP = '<span class="timestamp_value" id="quote_dateTime">'
TAGPRICE = '<span id="quote_val">'
TAGDATA = '<span class="data_data">'
MAXTHREADS = 10


# -----------------------------------------------------------------------------
def fetchprc_wsj(ticker, country):
    """
    Description:
        Fetch real-time or delayed prices from Wall Street Journal.
    Inputs:
        country - country symbol as defined by Wall Street Journal
        ticker  - ticker symbol as defined by Wall Street Journal
    Returns:
        A list of (price, timestamp) tuples.
    """
    url = BASEURL.format(country, ticker)
    http = urllib.request.urlopen(url).read().decode("utf-8")

    # --- timestamp
    try:
        idx0 = http.index(TAGTSAMP) + len(TAGTSAMP)
        idx1 = http[idx0:].index('</span>')
        tstamp = http[idx0:idx0+idx1]
    except ValueError:
        if "Quote Not Found" in http:
            raise ValueError("incorrect country code or ticker: "
                             "{0:s}/{1:s}".format(country, ticker))
        else:
            print(url)
            raise

    # --- price
    try:
        idx0 = http.index(TAGPRICE) + len(TAGPRICE)
        idx1 = http[idx0:].index('</span>')
        prc = http[idx0:idx0+idx1].replace(",", "")
    except ValueError:
        if "Quote Not Found" in http:
            raise ValueError("incorrect country code or ticker: "
                             "{0:s}/{1:s}".format(country, ticker))
        else:
            raise

    return float(prc), str(tstamp)


# -----------------------------------------------------------------------------
def fetchdiv_wsj(ticker, country):
    """
    Description:
        Fetch current dividend info from Wall Street Journal.
    Inputs:
        country - country symbol as defined by Wall Street Journal
        ticker  - ticker symbol as defined by Wall Street Journal
    Returns:
        A tuple (ex dividend date, dividend).
    """
    url = BASEURL.format(country, ticker)
    http = urllib.request.urlopen(url).read().decode("utf-8")

    idx = http.find('<h3>Dividends</h3>') + len('<h3>Dividends</h3>')
    http = http[idx:]

    if '"msg_empty"' in http:
        return None

    idx = http.find('Latest payment') + len('Latest payment')
    http = http[idx:]
    idx = http.find('</span>') + len('</span>')
    http = http[idx:]
    idx0 = http.find(TAGDATA) + len(TAGDATA)
    idx1 = http.find('</span>')

    field = http[idx0:idx1]
    fidx0 = field.find('<small')
    fidx1 = field.find('</small>') + len('</small>')

    try:
        div = float(field[:fidx0] + field[fidx1:])
    except ValueError:
        raise ValueError("Wrong dividend value for "
                         "{0:s}: {1:s}".format(ticker, http[idx0:idx1]))

    idx = http.find('Ex-Dividend Date') + len('Ex-Dividend Date')
    http = http[idx:]
    idx0 = http.find(TAGDATA) + len(TAGDATA)
    idx1 = http[idx0:].find('</span>') + idx0
    exdt = http[idx0:idx1]

    return exdt, div


# -----------------------------------------------------------------------------
def fetchmany_wsj(symbols, target=fetchprc_wsj):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAXTHREADS) as exe:
        data = list(exe.map(lambda s: target(*s), symbols))
    return data


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    from onyx.core import TableFilter
    from datafeeds_config import BBG_MAPPING

    # --- remove rows that don't have a Google symbol set
    TableFilter(BBG_MAPPING, lambda row: row["WSJ"] is not None)

    # --- sort by bbg symbol
    BBG_MAPPING.sort(["Bloomberg"])

    data = fetchmany_wsj([tuple(row["WSJ"].split(":")) for row in BBG_MAPPING])
    for row in zip(BBG_MAPPING.column("Bloomberg"), data):
        print(row)

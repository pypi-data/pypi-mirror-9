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

from onyx.core import Date

from matplotlib.finance import fetch_historical_yahoo

import collections
import urllib.error
import socket
import time

__all__ = ["YahooError", "fetch_yahoo_hist"]


###############################################################################
class YahooError(Exception):
    pass


# -----------------------------------------------------------------------------
def fetch_yahoo_hist(ticker, start=None,
                     end=None, dividends=False, fail_after=3):
    """
    Description:
        Fetch historical stock prices or dividends from Yahoo Finance.
    Inputs:
        ticker     - ticker symbol as defined by Yahoo Finance
        start      - the start date
        end        - the end date
        dividends  - if True, return historical dividends
        fail_after - fail after this number of unsuccesseful attempts
    Returns:
        A list of quotes where each quote is a namedtuple.
    """
    # --- at times, the query to yahoo server fails, hence the multi attempt
    #     procedure used here.
    start = start or Date(1980, 1, 1)
    end = end or Date.today()

    for n in range(fail_after):
        try:
            data = fetch_historical_yahoo(ticker, start, end,
                                          dividends=dividends)

        except (IOError, urllib.error.HTTPError, socket.error) as ex:
            if isinstance(ex, urllib.error.HTTPError) and ex.code == 404:
                raise YahooError("No available data for "
                                 "ticker '{0:s}' and date range "
                                 "{1!s} - {2!s}".format(ticker, start, end))

            # --- sometimes it helps waiting before fetching prices again
            time.sleep(1.0)

        # --- cast datatypes and format data
        quotes = [row.rstrip().split(",") for row in data]
        header = [q.replace(" ", "_") for q in quotes[0]]
        quote_cls = collections.namedtuple("quote", header)
        quotes = [quote_cls(Date.parse(quote[0]),
                            *[float(q) for q in quote[1:]])
                  for quote in sorted(quotes[1:])]

        return quotes

    # --- nothing worked, raise an exception
    raise YahooError("No response from yahoo server for ticker '{0:s}' "
                     "and date range {1!s} - {2!s}".format(ticker, start, end))

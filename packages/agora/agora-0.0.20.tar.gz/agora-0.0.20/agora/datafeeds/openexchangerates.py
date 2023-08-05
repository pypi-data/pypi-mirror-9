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

from onyx.core import Curve, Knot, DateRange

import urllib.request
import json
import pickle
import getpass
import os

BASE = "http://openexchangerates.org/api"

USER = getpass.getuser()
APP_ID = os.getenv("OPENEXCHANGERATES_APP_ID",
                   "8a439112054749a080ae72ce3114790c")
CACHE_FOLDER = os.getenv("FX_CACHE", os.path.join("/home", USER, "tmp"))


##-----------------------------------------------------------------------------
def __fetch_hist(date=None, app_id=APP_ID):
    if date is None:
        url = "{0:s}/latest.json?app_id={1:s}".format(BASE, app_id)
    else:
        url = "{0:s}/historical/{1:s}.json?"\
              "app_id={2:s}".format(BASE, date.strftime("%Y-%m-%d"), app_id)

    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    del data["disclaimer"]
    del data["license"]
    return data


##-----------------------------------------------------------------------------
def get_rate(date, ccy):
    file_name = os.path.join(CACHE_FOLDER,
                             date.strftime("fx_cache_%Y-%m-%d.dat"))
    try:
        with open(file_name, "rb") as cache_file:
            data = pickle.load(cache_file)

    except FileNotFoundError:
        data = __fetch_hist(date)
        with open(file_name, "wb") as cache_file:
            pickle.dump(data, cache_file, -1)

    return data["rates"][ccy]


##-----------------------------------------------------------------------------
def fetch_historical(ccy, start, end):
    """
    Description:
        Return historical prices for the ccy/USD cross, i.e. the value of
        1 unit of currency in US$ (sourced from www.openexchangerates.com).
    Inputs:
        ccy   - the currency crossed agains USD (ccy/USD)
        start - the start date
        end   - the end date
    Returns:
        A Curve.
    """
    cross = Curve()
    for date in DateRange(start, end, "+1d"):
        cross.data.append(Knot(date, 1.0 / get_rate(date, ccy)))
    return cross

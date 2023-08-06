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

from onyx.core import (UfoBase, GraphNodeVt, GetVal,
                       FloatField, ReferenceField, StringField, DictField)

__all__ = ["Exchange"]


###############################################################################
class Exchange(UfoBase):
    """
    Class used to represent an exchange or trading venue.
    """
    Denominated = ReferenceField(obj_type="Currency")
    Multiplier = FloatField(default=1.0)
    HolidayCalendar = ReferenceField(obj_type="HolidayCalendar")
    Country = ReferenceField(obj_type="Category")
    Region = ReferenceField(obj_type="Category")
    FullName = StringField(default="")
    Codes = DictField()
    TimeZone = StringField()
    MarketSession = StringField()

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        if self.HolidayCalendar is None:
            self.HolidayCalendar = GetVal(self.Denominated, "HolidayCalendar")

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Code(self, graph, platform="Bloomberg"):
        return graph(self, "Codes")[platform]


##-----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.unittest_utils import AddIfMissing
    import agora.system.ufo_currency as ufo_currency
    import agora.system.ufo_database as ufo_database
    import agora.system.ufo_holiday_calendar as ufo_holiday_calendar
    import agora.system.ufo_category as ufo_category

    ufo_database.prepare_for_test()
    ufo_holiday_calendar.prepare_for_test()
    ufo_currency.prepare_for_test()
    ufo_category.prepare_for_test()

    nyse_info = {
        "Name": "NYSE",
        "Denominated": "USD",
        "Country": "USA",
        "Region": "Nth. America",
        "FullName": "New York Stock Exchange",
        "Codes": {
            "Bloomberg": "US",
            "Google": "NYSE",
            "Yahoo": "",
            "WSJ": "US",
        },
    }

    london_info = {
        "Name": "London",
        "Denominated": "GBP",
        "Country": "United Kingdom",
        "Region": "Nth. Europe",
        "FullName": "London Stock Exchange",
        "Codes": {
            "Bloomberg": "LN",
            "Google": "LON",
            "Yahoo": "L",
            "WSJ": "UK",
        },
    }

    AddIfMissing(Exchange(**nyse_info))
    AddIfMissing(Exchange(**london_info))

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

from onyx.core import UfoBase, ReferenceField, StringField, GraphNodeVt

#import math

__all__ = ["Currency"]


###############################################################################
class Currency(UfoBase):
    """
    Class used to represent a currency and its discount curve.
    """
    DiscCurve = StringField()
    HolidayCalendar = ReferenceField(obj_type="HolidayCalendar")

    def __post_init__(self):
        self.DiscCurve = "DF-TS %{0:3s}".format(self.Name)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def ZeroCurve(self, graph):
        raise NotImplemented()

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def DiscountFactor(self, graph, from_date, to_date):
        return 1.0
       # zero_crv = graph(graph, self, "ZeroCurve")
       # ref_date = graph(graph, "Database", "MktDataDate")
       # return (math.exp(-CalcTerm(ref_date, from_date)*zero_crv[from_date]) *
       #         math.exp(CalcTerm(ref_date, to_date)*zero_crv[to_date]))


##-----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.unittest_utils import AddIfMissing
    import agora.system.ufo_database as ufo_database
    import agora.system.ufo_holiday_calendar as ufo_holiday_calendar

    ufo_database.prepare_for_test()
    ufo_holiday_calendar.prepare_for_test()

    AddIfMissing(Currency(Name="USD", HolidayCalendar="USD_CAL"))
    AddIfMissing(Currency(Name="EUR", HolidayCalendar="EUR_CAL"))
    AddIfMissing(Currency(Name="GBP", HolidayCalendar="GBP_CAL"))

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

from onyx.core import (GetVal, UfoBase, GraphNodeVt,
                       FloatField, ReferenceField, StringField, ListField)

from agora.risk.timeseries_functions import prices_for_risk

__all__ = ["Asset"]


###############################################################################
class Asset(UfoBase):
    """
    Base class used to provide a generic interface to all assets.
    """
    Symbol = StringField()
    Exchange = ReferenceField(obj_type="Exchange")
    Denominated = ReferenceField(obj_type="Currency")
    HolidayCalendar = ReferenceField(obj_type="HolidayCalendar")
    Multiplier = FloatField(default=1.0)
    Description = StringField(default="")
    RiskProxies = ListField()
    VolMatrix = StringField()
    VolModel = StringField()

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        # --- set defaults for attributes inherited from Exchange
        for attr in {"Denominated", "HolidayCalendar", "Multiplier"}:
            if getattr(self, attr) is None:
                setattr(self, attr, GetVal(self.Exchange, attr))

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Calc")
    def PricesForRisk(self, graph, start, end):
        return prices_for_risk(graph(self, "Name"), start, end)

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Calc")
    def SpotForRisk(self, graph):
        cross = "{0:3s}/USD".format(graph(self, "Denominated"))
        return graph(self, "Spot")*graph(cross, "Spot")

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

from onyx.core import UfoBase, StringField, ListField, ObjDbQuery, GraphNodeVt

import json

__all__ = ["Category"]

GET_ITEMS = "SELECT Name FROM Objects WHERE ObjType IN %s AND Data @> %s;"


###############################################################################
class Category(UfoBase):
    """
    Class used to collect instances of classes listed in ObjTypes that match
    the following pattern:
        graph(instance, "ValueType") == graph(self, "TargetValue")
    """
    ObjTypes = ListField()
    ValueType = StringField()
    TargetValue = StringField()

    # -------------------------------------------------------------------------
    def __post_init__(self):
        self.TargetValue = self.TargetValue or self.Name

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def Items(self, graph):
        parms = (graph(self, "ObjTypes"),
                 json.dumps({
                     graph(self, "ValueType"): graph(self, "TargetValue")}))
        results = ObjDbQuery(GET_ITEMS, parms, attr="fetchall")
        return sorted([res.name for res in results])


# -----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.unittest_utils import AddIfMissing

    AddIfMissing(Category(Name="Nth. America",
                          ObjTypes=["EquityAsset"], ValueType="Region"))
    AddIfMissing(Category(Name="Nth. Europe",
                          ObjTypes=["EquityAsset"], ValueType="Region"))
    AddIfMissing(Category(Name="USA",
                          ObjTypes=["EquityAsset"], ValueType="Country"))
    AddIfMissing(Category(Name="United Kingdom",
                          ObjTypes=["EquityAsset"], ValueType="Country"))

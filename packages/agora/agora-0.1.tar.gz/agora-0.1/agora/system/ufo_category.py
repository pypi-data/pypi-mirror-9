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

from onyx.core import UfoBase, StringField, ObjDbQuery, GraphNodeVt

import json

__all__ = ["Category"]

GET_ITEMS = "SELECT Name FROM Objects WHERE ObjType=%s AND Data @> %s;"


###############################################################################
class Category(UfoBase):
    """
    Class used to collect related objects names.
    """
    TargetType = StringField()
    TargetInstream = StringField()

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def Items(self, graph):
        parms = (graph(self, "TargetType"),
                 json.dumps({
                     graph(self, "TargetInstream"): graph(self, "Name")}))
        results = ObjDbQuery(GET_ITEMS, parms, attr="fetchall")
        return sorted([res.name for res in results])


##-----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.unittest_utils import AddIfMissing

    AddIfMissing(Category(Name="Nth. America",
                          TargetType="EquityAsset", TargetInstream="Region"))
    AddIfMissing(Category(Name="Nth. Europe",
                          TargetType="EquityAsset", TargetInstream="Region"))
    AddIfMissing(Category(Name="USA",
                          TargetType="EquityAsset", TargetInstream="Country"))
    AddIfMissing(Category(Name="United Kingdom",
                          TargetType="EquityAsset", TargetInstream="Country"))

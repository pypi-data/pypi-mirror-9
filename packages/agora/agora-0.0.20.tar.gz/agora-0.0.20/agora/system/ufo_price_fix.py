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
"""
Class used to represent price fixes (marks or settlement values).
"""

from onyx.core import (Date, Knot, Curve, ObjDbQuery, ObjNotFound,
                       GraphNodeVt, EvalBlock, SetDiddle)

from agora.system.ufo_archivable import Archivable
from agora.corelibs.ufo_functions import MktIndirectionFactory

__all__ = ["PriceFix"]

GET_MKS_QUERY = """
SELECT Date, Data->'_p_vt_data'->'Price' as Price
FROM Archive
WHERE Name=%s AND Date BETWEEN COALESCE(%s,%s) AND COALESCE(%s,%s)
ORDER BY Date;"""

GET_MOST_RECENT = """
SELECT MAX(Date) FROM Archive
WHERE Name=%s AND Date <= COALESCE(%s,%s)
"""


###############################################################################
class PriceFix(Archivable):
    ##-------------------------------------------------------------------------
    @MktIndirectionFactory
    def Price(self, graph):
        pass

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def PrcByDate(self, graph, date, strict=False):
        with EvalBlock() as eb:
            SetDiddle("Database", "MktDataDate", date, eb)
            SetDiddle("Database", "ForceStrict", strict, eb)
            return graph(self, "Price")

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def LastBefore(self, graph, date=None):
        parms = (graph(self, "Name"), date, Date.high_date())
        res = ObjDbQuery(GET_MOST_RECENT, parms, attr="fetchone")
        if res.max is None:
            raise ObjNotFound("{0:s} not found for any date earlier"
                              "than {1:s}".format(graph(self, "Name"), date))
        else:
            return res.max

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def PrcFixCurve(self, graph, start=None, end=None):
        parms = (graph(self, "Name"), start,
                 Date.low_date(), end, Date.high_date())
        crv = Curve.__new__(Curve)
        crv.knot_cls = Knot
        crv.data = [Knot(Date.parse(r[0]), r[1])
                    for r in ObjDbQuery(GET_MKS_QUERY, parms, attr="fetchall")]
        return crv


##-----------------------------------------------------------------------------
def prepare_for_test():
    import agora.system.ufo_database as ufo_database
    ufo_database.prepare_for_test()

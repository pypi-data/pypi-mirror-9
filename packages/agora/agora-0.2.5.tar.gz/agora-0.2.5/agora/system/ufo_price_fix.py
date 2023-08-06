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

from onyx.core import FloatField, GraphNodeVt, EvalBlock

from agora.system.ufo_archivable import Archivable
from agora.corelibs.ufo_functions import MktIndirectionFactory

__all__ = ["PriceFix"]


###############################################################################
class PriceFix(Archivable):
    """
    Class used to represent price fixes (marks or settlement values).
    """
    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Price(self, graph):
        pass

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def PrcByDate(self, graph, date, strict=False):
        with EvalBlock() as eb:
            eb.set_diddle("Database", "MktDataDate", date, eb)
            eb.set_diddle("Database", "ForceStrict", strict, eb)
            return graph(self, "Price")

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def PrcFixCurve(self, graph, start=None, end=None):
        return self.get_history("Price", start, end)


# -----------------------------------------------------------------------------
def prepare_for_test():
    import agora.system.ufo_database as ufo_database
    ufo_database.prepare_for_test()

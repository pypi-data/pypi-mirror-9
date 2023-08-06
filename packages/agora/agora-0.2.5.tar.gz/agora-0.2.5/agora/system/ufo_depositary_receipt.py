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

from onyx.core import ReferenceField, FloatField, GetVal, GraphNodeVt

from agora.corelibs.ufo_functions import InheritAsProperty
from agora.system.ufo_equity_asset import EquityAsset

__all__ = ["DepositaryReceipt"]

REPLACE = ["Country", "Region",
           "Sector", "Subsector", "RiskProxies"]


###############################################################################
@InheritAsProperty(REPLACE, "Parent")
class DepositaryReceipt(EquityAsset):
    """
    class used to represent a depositary receipt (GDR, ADR, etc).
    """
    # --- a reference to the local listing for this company
    Parent = ReferenceField(obj_type="EquityAsset")
    # --- one depositary receipt corresponds to these many shares in the
    #     local listing
    Conversion = FloatField(default=1.0)

    # -------------------------------------------------------------------------
    def __post_init__(self):
        # --- here we don't want to call EquityAsset's __post_init__ method
        #     but rather that of its super-class: this to avoid trying to set
        #     properties that have been inherited as properties.
        super(EquityAsset, self).__post_init__()

        exchange_code = GetVal(self.Exchange, "Code")

        self.Name = self.name_fmt.format(self.Symbol, exchange_code)

        # --- name of the time-series that store historical adjusted prices,
        #     historical closes (marks) and dividends
        fields = self.Symbol, exchange_code
        self.TimeSeries = "EQ-TS {0:s} {1:s}".format(*fields)
        self.Marks = "EQ-MKS {0:s} {1:s}".format(*fields)
        self.Dividends = "EQ-DIV {0:s} {1:s}".format(*fields)

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Spot(self, graph):
        """
        Return the official close value as of MktDataDate (or the most recent
        close if ForceStrict is False) in the Denominated currency.
        """
        parent = graph(self, "Parent")
        cross = "{0:3s}/USD".format(graph(parent, "Denominated"))
        spot_local = self.spot_local_ccy()
        return spot_local * graph(self, "Multiplier") / graph(cross, "Spot")

    # -------------------------------------------------------------------------
    def spot_local_ccy(self):
        """
        Return (off-graph) spot of the depositary receipt converted to the
        currency of the local listing.
        This gymnastic is needed to reflect the proper FX risk.
        """
        parent = GetVal(self, "Parent")
        den_to_usd = "{0:3s}/USD".format(GetVal(self, "Denominated"))
        loc_to_usd = "{0:3s}/USD".format(GetVal(parent, "Denominated"))
        spot = GetVal(GetVal(self, "Marks"), "Price")
        return spot * den_to_usd / loc_to_usd

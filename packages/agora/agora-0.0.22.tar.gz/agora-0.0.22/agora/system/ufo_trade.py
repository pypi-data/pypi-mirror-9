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

from onyx.core import(Structure, ObjDbQuery, GraphNodeVt, GetVal,
                      UfoBase, ReferenceField, IntField, FloatField, DateField,
                      StringField)

from agora.corelibs.tradable_api import AddByInference
from agora.tradables.ufo_forward_cash import ForwardCash

import random
import collections

__all__ = ["Trade", "TradeError"]


###############################################################################
Position = collections.namedtuple("Position", "Book Qty Unit UnitType NTD")


###############################################################################
class TradeError(Exception):
    pass


###############################################################################
class Trade(UfoBase):
    """
    Class used to represent trade objects in the system and their effects
    on positions.
    """
    SecurityTraded = ReferenceField(obj_type="TradableObj")
    TradeDate = DateField()
    TradeType = StringField()
    Quantity = IntField()
    Premium = FloatField(default=0.0)
    PremiumDen = ReferenceField(obj_type="Currency")
    SettlementDate = DateField()
    Party = ReferenceField(obj_type="Book")
    Counterparty = ReferenceField(obj_type="Book")
    Trader = ReferenceField(obj_type="Trader")
    Broker = ReferenceField(obj_type="Broker")
    BrokerageFee = FloatField(default=0.0)
    DealId = StringField()
    Marker = StringField()

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        # --- set object's name
        self.Name = Trade.random_name()

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def TradeInfo(self, graph):
        attrs = sorted(self.Instreams)
        return dict(zip(attrs, [graph(self, attr) for attr in attrs]))

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        trd_qty = graph(self, "Quantity")
        trd_type = graph(self, "TradeType")

        securities = graph(graph(self, "SecurityTraded"),
                           "ExpectedSecurities", trd_type)

        leaves = Structure()
        for sec_info in securities:
            qty = sec_info.Quantity*trd_qty
            leaves += qty*graph(sec_info.Security, "Leaves")

        # --- for buy and sell trades we include premium and brokerage
        if trd_type in ("Buy", "Sell"):
            trd_type = 1.0 if trd_type == "Buy" else -1.0

            den = graph(self, "PremiumDen")
            sett_dt = graph(self, "SettlementDate")
            cash = AddByInference(ForwardCash(den, sett_dt), in_memory=True)

            leaves -= trd_qty*Structure({cash.Name: graph(self, "Premium")})

            if graph(self, "Broker") is not None:
                leaves -= Structure({cash.Name: graph(self, "BrokerageFee")})

        return leaves

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        mtm = 0.0
        for leaf, qty in graph(self, "Leaves").items():
            mtm += qty*graph(leaf, "MktValUSD")
        return mtm

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        denominated = graph(self, "Denominated")
        spot_fx = graph("{0:3s}/USD".format(denominated, "Spot"))
        return graph(self, "MktValUSD") / spot_fx

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def PositionEffects(self, graph):
        # --- NB: leaves are now created and persisted in the database backend

        trd_qty = graph(self, "Quantity")
        trd_type = graph(self, "TradeType")
        cpty1 = graph(self, "Party")
        cpty2 = graph(self, "Counterparty")

        securities = graph(graph(self, "SecurityTraded"),
                           "ExpectedSecurities", trd_type)
        poseff = []
        for sec_info in securities:
            try:
                ntd = graph(sec_info.Security, "NextTransactionDate")
            except AttributeError:
                ntd = graph(self, "SettlementDate")

            leaf = AddByInference(sec_info.Security)
            qty = sec_info.Quantity*trd_qty
            poseff += [
                Position(cpty1, qty, leaf.Name, leaf.ObjType, ntd),
                Position(cpty2, -qty, leaf.Name, leaf.ObjType, ntd)
            ]

        # --- for buy and sell trades we include premium and brokerage
        if trd_type in ("Buy", "Sell"):
            trd_type = 1.0 if trd_type == "Buy" else -1.0

            brokr = graph(self, "Broker")
            premium = graph(self, "Premium")
            den = graph(self, "PremiumDen")
            sett_dt = graph(self, "SettlementDate")

            cash = AddByInference(ForwardCash(den, sett_dt))
            cash_ntd = graph(cash, "NextTransactionDate")

            if premium != 0.0:
                poseff += [
                    Position(cpty1, -trd_qty*premium,
                             cash.Name, cash.ObjType, cash_ntd),
                    Position(cpty2, trd_qty*premium,
                             cash.Name, cash.ObjType, cash_ntd)
                ]

            if brokr is not None:
                fee = graph(self, "BrokerageFee")
                poseff += [
                    Position(cpty1, -fee, cash.Name, cash.ObjType, cash_ntd),
                    Position(brokr, fee, cash.Name, cash.ObjType, cash_ntd)
                ]

        return poseff

    ##-------------------------------------------------------------------------
    def delete(self):
        if GetVal("Database", "TradesDeletable"):
            ObjDbQuery("DELETE FROM PosEffects "
                       "WHERE Trade = %s", parms=(self.Name,))
        else:
            raise TradeError("Trying to delete a trade without permissions")

    ##-------------------------------------------------------------------------
    @classmethod
    def random_name(cls):
        return "TmpTrade-{0:>06d}".format(random.randrange(0, 1000000, 1))

    ##-------------------------------------------------------------------------
    @classmethod
    def format_name(cls, date, trd_id):
        return "TRD {0!s} {1:8s}".format(date, trd_id)

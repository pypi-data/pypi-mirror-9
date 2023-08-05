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

from onyx.core import(Date, Structure, GetObj, ObjDbQuery, GraphNodeVt, GetVal,
                      UfoBase, ReferenceField, IntField, FloatField, DateField,
                      StringField, IntSelectField)

from agora.corelibs.tradable_api import AddByInference, TradableObj
from agora.corelibs.date_functions import DateOffset

from agora.system.ufo_Currency import Currency
from agora.tradables.ufo_forward_cash import ForwardCash

from agora.system.ufo_book import Book
from agora.system.ufo_trader import Trader
from agora.system.ufo_broker import Broker

import random
import collections

CURRENT_DATE = DateOffset(Date.today(), "+0b")
BASE_NAME = "TRD {0:s}-{1:>012d}"


###############################################################################
Position = collections.namedtuple("Position",
                                  "Book Qty Unit UnitType NTD Status")


###############################################################################
class TradeError(Exception):
    pass


###############################################################################
class Trade(UfoBase):
    """
    Class used to represent trade objects in the system and their effects
    on positions.

    TradeType:       buy (+1) or sell (-1)
    Quantity:        number of units of security traded
    SettledQuantity: number of units of security traded that have settled

    """
    SecurityTraded = ReferenceField(obj_type=TradableObj)
    TradeDate = DateField(default=CURRENT_DATE)
    TradeType = IntSelectField(default=1, options=[1,-1])
    Quantity = IntField(default=1)
    SettledQuantity = IntField(default=0)
    Premium = FloatField(default=0.0)
    PremiumDen = ReferenceField(default="USD", obj_type=Currency)
    SettlementDate = DateField(default=CURRENT_DATE)
    Party = ReferenceField(obj_type=Book)
    Counterparty = ReferenceField(obj_type=Book)
    Trader = ReferenceField(obj_type=Trader)
    Broker = ReferenceField(obj_type=Broker)
    BrokerageFee = FloatField(default=0.0)
    DealId = StringField()

    ##-------------------------------------------------------------------------
    def __post_init__(self):
        # --- further input validation
        if self.SettledQuantity > self.Quantity:
            raise TradeError("Settled quantity ({0:d}) "
                             "available quantity ({1:d})".
                             format(self.SettledQuantity, self.Quantity))

        # --- set object's name
        self.Name = Trade.random_name()

        # --- these are attributes than are set by the trade_api
        self.Marker = "HEAD"

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def OpenQuantity(self, graph):
        return graph(self, "Quantity") - graph(self, "SettledQuantity")

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def TradeInfo(self, graph):
        return dict(zip(self.Instreams,
                        [graph(self, attr) for attr in self.Instreams]))

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        sett_qty = graph(self, "SettledQuantity")
        trd_qty = graph(self, "TradeType")*graph(self, "Quantity")
        open_qty = graph(self, "TradeType")*graph(self, "OpenQuantity")

        den = graph(self, "PremiumDen")
        sett_dt = graph(self, "SettlementDate")
        cash = AddByInference(ForwardCash(den, sett_dt), in_memory=True)

        leaves = open_qty*graph(graph(self, "SecurityTraded"), "Leaves")
        leaves -= trd_qty*Structure({cash.Name: graph(self, "Premium")})

        if sett_qty > 0:
            sec = graph(self, "SecurityTraded")
            sett_qty *= graph(self, "TradeType")
            leaves -= sett_qty*graph(sec, "ExpectedSecurities")

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
    @property
    def PositionEffects(self):
        # --- NB: leaves are now created and persisted in the database backend

        trd_type = self.TradeType
        sett_qty = self.SettledQuantity
        trd_qty = trd_type*self.Quantity
        open_qty = trd_type*self.OpenQuantity
        sett_dt = self.SettlementDate
        sec = self.SecurityTraded

        cash = AddByInference(ForwardCash(self.PremiumDen, sett_dt))
        cash_ntd = GetVal(cash, "NextTransactionDate")
        premium = self.Premium

        cpty1 = self.Party
        cpty2 = self.Counterparty
        brokr = self.Broker

        poseff = []

        # --- open leaves
        for leaf_name, qty in GetVal(sec, "Leaves").items():
            try:
                ntd = GetVal(leaf_name, "NextTransactionDate")
            except AttributeError:
                ntd = sett_dt

            leaf = AddByInference(GetObj(leaf_name))
            poseff += [
                Position(cpty1, open_qty*qty,
                         leaf.Name, leaf.ObjType, ntd, "O"),
                Position(cpty2, -open_qty*qty,
                         leaf.Name, leaf.ObjType, ntd, "O")
            ]

        # --- settled leaves (if any)
        if sett_dt > 0:
            sett_dt *= -trd_type
            for leaf_name, qty in GetVal(sec, "ExpectedSecurities").items():
                try:
                    ntd = GetVal(leaf_name, "NextTransactionDate")
                except AttributeError:
                    ntd = None

                leaf = AddByInference(GetObj(leaf_name))
                poseff += [
                    Position(cpty1, sett_qty*qty,
                             leaf.Name, leaf.ObjType, ntd, "S"),
                    Position(cpty2, -sett_qty*qty,
                             leaf.Name, leaf.ObjType, ntd, "S")
                ]

        if premium != 0.0:
            poseff += [
                Position(cpty1, -trd_qty*premium,
                         cash.Name, cash.ObjType, cash_ntd, "O"),
                Position(cpty2, trd_qty*premium,
                         cash.Name, cash.ObjType, cash_ntd, "O")
            ]

        if brokr is not None:
            fee = GetVal(self, "BrokerageFee")
            poseff += [
                Position(cpty1, -fee, cash.Name, cash.ObjType, cash_ntd, "O"),
                Position(brokr, fee, cash.Name, cash.ObjType, cash_ntd, "O")
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

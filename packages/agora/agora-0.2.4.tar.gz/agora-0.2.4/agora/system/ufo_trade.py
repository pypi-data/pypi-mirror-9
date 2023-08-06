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
                      StringField, SelectField)

from agora.corelibs.tradable_api import AddByInference
from agora.corelibs.date_functions import DateOffset
from agora.tradables.ufo_forward_cash import ForwardCash
from agora.risk.core_functions import WithRiskValueTypes

import random
import collections

__all__ = ["Trade", "TradeError"]


###############################################################################
Position = collections.namedtuple("Position", "Book Qty Unit UnitType NTD")


###############################################################################
class TradeError(Exception):
    pass


###############################################################################
@WithRiskValueTypes
class Trade(UfoBase):
    """
    Class used to represent trade objects in the system and their effects
    on positions.
    """
    SecurityTraded = ReferenceField(obj_type="TradableObj")
    TradeDate = DateField()
    TradeType = StringField()
    Quantity = IntField(positive=True)
    UnitPrice = FloatField(default=0.0, positive=True)
    PaymentUnit = ReferenceField(obj_type="Currency")
    SettlementDate = DateField()
    Party = ReferenceField(obj_type="Book")
    Counterparty = ReferenceField(obj_type="Book")
    Trader = ReferenceField(obj_type="Trader")
    Broker = ReferenceField(obj_type="Broker")
    BrokerageFee = FloatField(default=0.0, positive=True)
    OtherCosts = FloatField(default=0.0, positive=True)
    DealId = StringField()
    Marker = SelectField(options=["HEAD", "AMENDED", "BACKOUT", "DELETE"])

    # -------------------------------------------------------------------------
    def __post_init__(self):
        # --- set object's name if not set already
        self.Name = self.Name or Trade.random_name()

        # --- set default values
        self.PaymentUnit = self.PaymentUnit or "USD"

        if self.SettlementDate is None:
            cal = GetVal(self.PaymentUnit, "HolidayCalendar")
            self.SettlementDate = DateOffset(self.TradeDate, "+2b", cal)

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Denominated(self, graph):
        """
        A trade is denominated in the PaymentUnit currency.
        """
        return graph(self, "PaymentUnit")

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def TradeInfo(self, graph):
        attrs = sorted(self._json_fields)
        return dict(zip(attrs, [graph(self, attr) for attr in attrs]))

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        trd_qty = graph(self, "Quantity")
        trd_type = graph(self, "TradeType")

        securities = graph(graph(self, "SecurityTraded"),
                           "ExpectedSecurities", trd_type)

        leaves = Structure()
        for sec_info in securities:
            qty = sec_info["Quantity"]*trd_qty
            leaves += qty*graph(sec_info["Security"], "Leaves")

        # --- for buy and sell trades we include premium and brokerage
        if trd_type in ("Buy", "Sell"):
            qty = trd_qty*(1.0 if trd_type == "Buy" else -1.0)

            ccy = graph(self, "PaymentUnit")
            sett_dt = graph(self, "SettlementDate")
            cash = ForwardCash(Currency=ccy, PaymentDate=sett_dt)
            cash = AddByInference(cash, in_memory=True)

            leaves -= qty*Structure({cash.Name: graph(self, "UnitPrice")})
            leaves -= Structure({cash.Name: graph(self, "OtherCosts")})

            if graph(self, "Broker") is not None:
                leaves -= Structure({cash.Name: graph(self, "BrokerageFee")})

        return leaves

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktValUSD(self, graph):
        mtm = 0.0
        for leaf, qty in graph(self, "Leaves").items():
            mtm += qty*graph(leaf, "MktValUSD")
        return mtm

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def MktVal(self, graph):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
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
                ntd = graph(sec_info["Security"], "NextTransactionDate")
            except AttributeError:
                ntd = graph(self, "SettlementDate")

            sec = AddByInference(sec_info["Security"], in_memory=False)
            qty = sec_info["Quantity"]*trd_qty
            poseff += [
                Position(cpty1, qty, sec.Name, sec.ObjType, ntd),
                Position(cpty2, -qty, sec.Name, sec.ObjType, ntd)
            ]

        # --- for buy and sell trades we include premium and brokerage
        if trd_type in ("Buy", "Sell"):
            trd_qty *= 1.0 if trd_type == "Buy" else -1.0

            brokr = graph(self, "Broker")
            price = graph(self, "UnitPrice")
            ccy = graph(self, "PaymentUnit")
            sett_dt = graph(self, "SettlementDate")

            cash = ForwardCash(Currency=ccy, PaymentDate=sett_dt)
            cash = AddByInference(cash, in_memory=False)
            cash_ntd = graph(cash, "NextTransactionDate")

            if price > 0.0:
                poseff += [
                    Position(cpty1, -trd_qty*price,
                             cash.Name, cash.ObjType, cash_ntd),
                    Position(cpty2, trd_qty*price,
                             cash.Name, cash.ObjType, cash_ntd)
                ]

            other_costs = graph(self, "OtherCosts")

            if other_costs > 0.0:
                poseff += [
                    Position(cpty1, -other_costs,
                             cash.Name, cash.ObjType, cash_ntd),
                    Position("TAXNCOSTS", other_costs,
                             cash.Name, cash.ObjType, cash_ntd)
                ]

            if brokr is not None:
                fee = graph(self, "BrokerageFee")
                poseff += [
                    Position(cpty1, -fee, cash.Name, cash.ObjType, cash_ntd),
                    Position(brokr, fee, cash.Name, cash.ObjType, cash_ntd)
                ]

        return poseff

    # -------------------------------------------------------------------------
    def delete(self):
        if GetVal("Database", "TradesDeletable"):
            ObjDbQuery("DELETE FROM PosEffects "
                       "WHERE Trade = %s", parms=(self.Name,))
        else:
            raise TradeError("Trying to delete a trade without permission")

    # -------------------------------------------------------------------------
    @classmethod
    def random_name(cls):
        return "TmpTrade-{0:>06d}".format(random.randrange(0, 1000000, 1))

    # -------------------------------------------------------------------------
    @classmethod
    def format_name(cls, date, trd_id):
        return "TRD {0!s} {1:8s}".format(date, trd_id)


# -----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import Date
    from agora.corelibs.unittest_utils import AddIfMissing

    import agora.system.ufo_book as ufo_book
    import agora.system.ufo_trader as ufo_trader
    import agora.system.ufo_broker as ufo_broker
    import agora.tradables.ufo_equity_cash as ufo_equity_cash
    import agora.tradables.ufo_equity_cfd as ufo_equity_cfd
    import agora.tradables.ufo_forward_cash as ufo_forward_cash

    books = ufo_book.prepare_for_test()
    traders = ufo_trader.prepare_for_test()
    brokers = ufo_broker.prepare_for_test()
    eqcash = ufo_equity_cash.prepare_for_test()
    eqcfds = ufo_equity_cfd.prepare_for_test()

    ufo_forward_cash.prepare_for_test()

    trades = [
        # --- this is a cash trade
        {
            "SecurityTraded": eqcash[0],
            "TradeDate": Date.today(),
            "TradeType": "Sell",
            "Quantity": 1000,
            "Party": books[0],
            "Counterparty": books[2],
            "Trader": traders[0],
            "Broker": brokers[0],
            "UnitPrice": 9.1*1.5/1.15,
            "PaymentUnit": "EUR",
        },
        # --- this is a CFD trade
        {
            "SecurityTraded": eqcfds[0],
            "TradeDate": Date.today(),
            "TradeType": "Sell",
            "Quantity": 1000,
            "Party": books[0],
            "Counterparty": books[2],
            "Trader": traders[0],
            "Broker": brokers[0],
        }
    ]
    trades = [AddIfMissing(Trade(**trade_info)) for trade_info in trades]

    return [trade.Name for trade in trades]

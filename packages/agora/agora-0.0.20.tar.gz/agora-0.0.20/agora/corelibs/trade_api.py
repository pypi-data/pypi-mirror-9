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

from onyx.core import (Date, Structure,
                       AddObj, GetObj, UpdateObj, ObjDbQuery, ObjNotFound,
                       Transaction, ExistsInDatabase,
                       GetVal, SetVal, PurgeObj)

from agora.corelibs.tradable_api import AddByInference
from agora.system.ufo_trade import Trade, TradeError
from agora.system.ufo_trader import Trader
from agora.system.ufo_book import Book
from agora.system.ufo_broker import Broker

__all__ = [
    "TradeError",
    "TradeCommit",
    "TradeDelete",
    "ChildrenByBook",
    "TradesBy",
    "ValidDealIds",
    "TradeDiff",
]

# --- set of valid trade markers
markers = {"HEAD", "AMENDED", "BACKOUT", "DELETE"}


# --- templates for common queries

QUERY_GETIDS = """
SELECT COUNT( DISTINCT( Trade ) ), COUNT( DISTINCT( DealId ) )
FROM PosEffects;"""

QUERY_INSERT_POSEFF = """
INSERT INTO PosEffects
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""

QUERY_DELETE_POSEFF = """
DELETE FROM PosEffects WHERE Trade = %s;"""

QUERY_KIDSBYBOOK = """
SELECT Unit, SUM( Qty )
FROM PosEffects WHERE Book = %s AND {0:s} <= %s
GROUP BY Unit;"""

QUERY_VALID_IDS = """
SELECT DISTINCT( DealId ) FROM PosEffects ORDER BY DealId;"""


##-----------------------------------------------------------------------------
def UniqueTradeIds():
    """
    Get next trade ID from the database.
    """
    trd_id, deal_id = ObjDbQuery(QUERY_GETIDS, attr="fetchone")

    trd_id = 1 if trd_id is None else trd_id + 1
    deal_id = 1 if deal_id is None else deal_id + 1

    return trd_id, deal_id


##-----------------------------------------------------------------------------
def PreTradeCompliance(trade):
    """
    Description:
        This function is ment to raise a TradeError exception for any violation
        of pre-trade compliance checks.
    Inpots:
        trade - the trade to be checked
    Returns:
        None.
    """
    # --- price validation
    GetVal(trade, "MktValUSD")

    name = GetVal(trade, "Trader")
    try:
        obj = GetObj(name)
        if not isinstance(obj, Trader):
            raise TradeError("{0:s} is not a valid Trader".format(obj.Name))
    except ObjNotFound:
        raise TradeError("Trader set to {0:s}: "
                         "object not found in database".format(name))

    for attr in {"Party", "Counterparty"}:
        name = GetVal(trade, attr)
        try:
            obj = GetObj(name)
            if not isinstance(obj, Book):
                raise TradeError("{0:s} is not "
                                 "a valid {1:s}".format(obj.Name, attr))
        except ObjNotFound:
            raise TradeError("{0:s} set to {1:s}: "
                             "object not found in database".format(attr, name))

    if GetVal(trade, "Broker") is not None:
        name = GetVal(trade, "Broker")
        try:
            obj = GetObj(name)
            if not isinstance(obj, Broker):
                raise TradeError("{0:s} is not "
                                 "a valid Broker".format(obj.Name))
        except ObjNotFound:
            raise TradeError("Broker set to {0:s}: "
                             "object not found in database".format(name))


##-------------------------------------------------------------------------
def TradeCommit(trade, callback=None):
    """
    Description:
        ...
    Inputs:
        trade    - the trade to commit
        callback - ...
    Returns:
        A Trade instance.
    """
    # --- clone security traded: AddByInference is needed to generate a new
    #     ImpliedName if any of the Instreams have been changed.
    sec_name = GetVal(trade.Name, "SecurityTraded")
    sec = AddByInference(GetObj(sec_name).Clone(name=sec_name))

    if ExistsInDatabase(trade.Name):
        info = GetVal(trade, "TradeInfo")
        info["SecurityTraded"] = sec.Name
        return TradeAmend(trade, callback, **info)
    else:
        SetVal(trade, "SecurityTraded", sec.Name)
        return TradeCreate(callback, **GetVal(trade, "TradeInfo"))


##-----------------------------------------------------------------------------
def TradeCreate(callback=None, **trd_info):
    """
    This function should not be called directly. Use TradeCommit instead.
    """
    # --- keep track of affected books
    books = set()

    trd_id, deal_id = UniqueTradeIds()

    # --- create Trade object and use the trdId to generate the DealId
    trd_info["DealId"] = "ID{0:>012d}".format(deal_id)
    trade = Trade(**trd_info)
    trade.Name = trade.BaseName.format(Date.today().strftime("%Y%m%d"), trd_id)
    trade.Marker = "HEAD"

    with Transaction("InsertTrade"):
        trade = AddObj(trade)
        PreTradeCompliance(trade)

        for pos in trade.PositionEffects:
            books.add(pos.Book)
            ObjDbQuery(QUERY_INSERT_POSEFF,
                       parms=(trade.TimeCreated, trade.TradeDate, pos.Book,
                              trade.Trader, pos.Qty, pos.Unit, pos.UnitType,
                              pos.Status, trade.Name, trade.DealId, pos.NTD))

    # --- on success, execute the callback
    if callback is not None:
        callback(books)

    return trade


##-----------------------------------------------------------------------------
def TradeAmend(trade, callback, **trd_info):
    """
    This function should not be called directly. Use TradeCommit instead.
    """
    # --- reload security: this is needed to avoid basing decisions on
    #     attribute values that were set in memory
    trade = GetObj(trade.Name, refresh=True)

    # --- need to amend?
    same = True
    for attr, value in trd_info.items():
        same = (value == getattr(trade, attr))
        if not same:
            break
    if same:
        raise ValueError("TradeAmend, found nothing to amend.")

    # --- keep track of affected books
    books = set()

    if trade.TimeCreated >= Date.today():
        # --- same day amendment: execute in-place update

        for attr, value in trd_info.items():
            setattr(trade, attr, value)

        with Transaction("AmendTrade"):
            UpdateObj(trade)

            # --- Trade validation: if we fail here the whole transaction is
            #                       rolled-back
            PreTradeCompliance(trade)

            # --- delete existing positions for this trade
            ObjDbQuery(QUERY_DELETE_POSEFF, (trade.Name,))

            # --- insert new position effects
            for pos in trade.PositionEffects:
                books.add(pos.Book)
                ObjDbQuery(QUERY_INSERT_POSEFF,
                           parms=(
                               trade.TimeCreated, trade.TradeDate, pos.Book,
                               trade.Trader, pos.Qty, pos.Unit, pos.UnitType,
                               pos.Status, trade.Name, trade.DealId, pos.NTD))

    else:
        # --- previous day amendment: book a backout trade and then a new trade

        trd_id, _ = UniqueTradeIds()
        today = Date.today().strftime("%Y%m%d")

        with Transaction("AmendTrade"):
            trade.Marker = "AMENDED"
            UpdateObj(trade)

            backout = trade.Clone()
            backout.Name = trade.BaseName.format(today, trd_id)
            backout.Marker = "BACKOUT"

            newtrade = trade.Clone()
            newtrade.Name = trade.BaseName.format(today, trd_id + 1)
            newtrade.DealId = trade.DealId
            newtrade.Marker = "HEAD"

            for attr, value in trd_info.items():
                setattr(newtrade, attr, value)

            AddObj(backout)
            AddObj(newtrade)

            # --- Trades validation: if we fail here the whole transaction is
            #     rolled-back
            PreTradeCompliance(trade)
            PreTradeCompliance(backout)
            PreTradeCompliance(newtrade)

            # --- update position effects table:
            # ---  1) first the back-out trade: quantities are flipped to
            #         offset original trade
            for pos in backout.PositionEffects:
                books.add(pos.Book)
                ObjDbQuery(QUERY_INSERT_POSEFF,
                           parms=(
                               backout.TimeCreated, trade.TradeDate, pos.Book,
                               backout.Trader, -pos.Qty, pos.Unit,
                               pos.UnitType, pos.Status, backout.Name,
                               backout.DealId, pos.NTD))

            # ---  2) then the new trade with the amendments
            for pos in newtrade.PositionEffects:
                books.add(pos.Book)
                ObjDbQuery(QUERY_INSERT_POSEFF,
                           parms=(
                               newtrade.TimeCreated, newtrade.TradeDate,
                               pos.Book, newtrade.Trader, pos.Qty, pos.Unit,
                               pos.UnitType, pos.Status, pos.Unit,
                               newtrade.Name, newtrade.DealId, pos.NTD))

        trade = newtrade

    # --- on success, execute the callback
    if callback is not None:
        callback(books)

    return trade


##-----------------------------------------------------------------------------
def TradeDelete(trade, callback=None):
    """
    Description:
        ...
    Inputs:
        trade    - the trade to delete
        callback - ...
    Returns:
        None.
    """
    # --- reload security: this is needed to avoid basing decisions on
    #     attribute values that were set in memory
    trade = GetObj(trade.Name, refresh=True)

    # --- TradeDelete can only delete head-trades
    if trade.Marker != "HEAD":
        raise TradeError("Only head-trades can be deleted. "
                         "Marker is {0:s}".format(trade.Marker))

    # --- get all trades by DealId
    trades = TradesBy(deal_id=trade.DealId, head_only=False)

    # --- keep track of affected books
    books = set()

    if trade.TimeCreated >= Date.today():
        # --- same day delete: there are two sub-cases

        if len(trades) == 1:
            # --- case 1: delete object (all postion effectes are taken care
            #             of automatically)
            books.update({trade.Party, trade.Counterparty, trade.Broker})
            with Transaction("DeleteTrade"):
                PurgeObj(trade.Name)

        elif len(trades) >= 3:
            # --- case 2: delete last two objects and re-mark the amended one
            #             as "HEAD"
            head = GetObj(trades[-1], refresh=True)
            backout = GetObj(trades[-2], refresh=True)
            amended = GetObj(trades[-3], refresh=True)

            # --- check that markers conform to expectation
            if not head.Marker == "HEAD":
                raise TradeError("Wrong Marker for trade {0:s} is {1:s} "
                                 "instead of HEAD".format(head, head.Marker))
            if not backout.Marker == "BACKOUT":
                raise TradeError("Wrong Marker for trade {0:s} is {1:s} "
                                 "instead of BACKOUT".format(backout,
                                                             backout.Marker))
            if not amended.Marker == "AMENDED":
                raise TradeError("Wrong Marker for trade {0:s} is {1:s} "
                                 "instead of AMENDED".format(amended,
                                                             amended.Marker))

            books.update({head.Party, head.Counterparty, head.Broker})
            books.update({backout.Party, backout.Counterparty, backout.Broker})

            with Transaction("DeleteTrade"):
                PurgeObj(head.Name)
                PurgeObj(backout.Name)

                amended.Marker = "HEAD"
                UpdateObj(amended)

            trade = amended

        else:
            # --- we should never have two trades for a given DealId
            raise RuntimeError("Positions are messed up for {0:s}, "
                               "{1:d}".format(trade.DealId, len(trades)))

    else:
        # --- previous day delete: book backout and mark trade as deleted
        trd_id, _ = UniqueTradeIds()
        today = Date.today().strftime("%Y%m%d")

        trade.Marker = "DELETED"
        backout = trade.Clone()
        backout.Name = trade.BaseName.format(today, trd_id)
        backout.Marker = "BACKOUT"

        with Transaction("DeleteTrade"):
            UpdateObj(trade)
            AddObj(backout)

            # --- Trades validation: if we fail here the whole transaction is
            #     rolled-back
            PreTradeCompliance(backout)

            # --- now update position effects
            for pos in backout.PositionEffects:
                books.add(pos.Book)
                ObjDbQuery(QUERY_INSERT_POSEFF,
                           parms=(
                               backout.TimeCreated, pos.Book, backout.Trader,
                               -pos.Qty, pos.Unit, pos.UnitType, pos.Status,
                               backout.Name, backout.DealId, pos.NTD))

        trade = backout

    # --- on success, execute the callback
    if callback is not None:
        callback(books)

    del trade


##-----------------------------------------------------------------------------
def ChildrenByBook(book, pos_date, by_time_created=False):
    """
    Description:
        Return all children of a given book as of a given date.
    Inputs:
        book            - the book
        pos_date        - the positions date
        by_time_created - if True, amendments are reflected on the date they
                          were booked, not on the date of the original trade.
    Returns:
        A Structure.
    """
    if by_time_created:
        query = QUERY_KIDSBYBOOK.format("TimeCreated")
    else:
        query = QUERY_KIDSBYBOOK.format("TradeDate")

    rows = ObjDbQuery(query, parms=(book, pos_date.EOD()), attr="fetchall")
    children = Structure()
    for row in rows:
        # --- exclude children with zero quantity
        if row[1] != 0.0:
            children[row[0]] = int(row[1])

    return children


##-----------------------------------------------------------------------------
def TradesBy(book=None, trader=None, deal_id=None,
             date_range=None, ntd=None, head_only=True):
    """
    Description:
        Return all trades matching the given criteria.
    Inputs:
        book       - ...
        trader     - ...
        deal_id    - ...
        date_range - a tuple of start and end date
        ntd        - ...
        head_only  - ...
    Returns:
        A list of trade names.
    """
    extquery = []
    criteria = []

    if book is not None:
        extquery.append("Book=%s")
        criteria.append(book)

    if trader is not None:
        extquery.append("Trader=%s")
        criteria.append(trader)

    if deal_id is not None:
        extquery.append("DealId=%s")
        criteria.append(deal_id)

    if date_range is not None:
        extquery.append("TrdDate BETWEEN %s AND %s")
        criteria.append(date_range[0])
        criteria.append(date_range[1])

    if ntd is not None:
        extquery.append("NTD=%s")
        criteria.append(ntd)

    if len(criteria):
        query = """SELECT Trade FROM PosEffects WHERE {0:s}
                   GROUP BY Trade
                   ORDER BY Trade;""".format(" AND ".join(extquery))

        rows = ObjDbQuery(query, parms=criteria, attr="fetchall")

    else:
        query = """SELECT Trade FROM PosEffects
                   GROUP BY Trade
                   ORDER BY Trade;"""

        rows = ObjDbQuery(query, attr="fetchall")

    if head_only:
        return [r[0] for r in rows if GetVal(r[0], "Marker") == "HEAD"]
    else:
        return [r[0] for r in rows]


##-----------------------------------------------------------------------------
def ValidDealIds():
    """
    Description:
    Inputs:
    Returns:
    """
    return [r[0] for r in ObjDbQuery(QUERY_VALID_IDS, attr="fetchall")]


##-----------------------------------------------------------------------------
def TradeDiff(trade1, trade2):
    """
    Description:
    Inputs:
    Returns:
    """
    str1 = GetVal(trade1, "TradeInfo")
    str2 = GetVal(trade2, "TradeInfo")
    diffs = {}
    for key, value in str1.items():
        if str2[key] != value:
            diffs[key] = (value, str2[key])
    return diffs

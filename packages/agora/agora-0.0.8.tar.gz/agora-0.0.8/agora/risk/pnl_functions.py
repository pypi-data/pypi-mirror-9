###############################################################################
#
#  Agora Portfolio & Risk Management System
#
#  Description: risk monitoring
#
#  File Created: 01 Jan 2015
#  Author: Carlo Sbraccia
#
###############################################################################

from Abacus.Datatypes.Structure import Structure
from Agora.LIB_PortfolioIOFns import PortfolioHierarchy

import ftplib

__all__ = [ "PnL", "LoadPnLFromFtp", "LoadMtMFromFtp" ]

################################################################################
##  PnL
##------------------------------------------------------------------------------
class PnL( object ):
    __slots__ = [ "DTD", "MTD", "YTD" ]
    def __init__( self, dtd, mtd, ytd ):
        self.DTD = dtd
        self.MTD = mtd
        self.YTD = ytd

    def __add__( self, other ):
        return self.__class__( self.DTD + other.DTD,
                               self.MTD + other.MTD,
                               self.YTD + other.YTD )

    def __iadd__( self, other ):
        self.DTD += other.DTD
        self.MTD += other.MTD
        self.YTD += other.YTD
        return self

    def __str__( self ):
        return "%12.2f,%12.2f,%12.2f" % ( self.DTD, self.MTD, self.YTD )

################################################################################
##  LoadPnLFromFtp
##------------------------------------------------------------------------------
def LoadPnLFromFtp( host, user, passwd, date, query = None, skip = None ):

    query = query or {}
    skip = skip or {}

    pnlByBook = Structure()

    # --- load current positions from ftp
    ftp = ftplib.FTP( host, user, passwd )
    cmd = date.strftime( "RETR Positions_Extract_%Y%m%d.csv" )

    try:
        report = []
        ftp.retrlines( cmd, lambda r: report.append( r ) )
    except ftplib.error_perm:
        return pnlByBook

    tot = PnL( 0.0, 0.0, 0.0 )

    for row in report[1:]:
        fields = row.rstrip().split( "," )

        port, book, strat = PortfolioHierarchy( fields )

        # --- skip if it doesn't match query
        if "port"  in query and not  port in  query["port"]: continue
        if "book"  in query and not  book in  query["book"]: continue
        if "strat" in query and not strat in query["strat"]: continue

        # --- skip if in skipset
        if "port"  in skip and  port in  skip["port"]: continue
        if "book"  in skip and  book in  skip["book"]: continue
        if "strat" in skip and strat in skip["strat"]: continue

        dtd = float( fields[18] ) if fields[18] != "" else 0.0
        mtd = float( fields[19] ) if fields[19] != "" else 0.0
        ytd = float( fields[20] ) if fields[20] != "" else 0.0

        pnl  = PnL( dtd, mtd, ytd )
        tot += pnl

        try:
            pnlByBook[book] += pnl
        except KeyError:
            pnlByBook[book]  = pnl

    pnlByBook["Total"] = tot

    return pnlByBook

################################################################################
##  LoadMtMFromFtp
##------------------------------------------------------------------------------
def LoadMtMFromFtp( host, user, passwd, date, query = None, skip = None ):

    query = query or {}
    skip = skip or {}

    # --- load current positions from ftp
    ftp = ftplib.FTP( host, user, passwd )
    cmd = date.strftime( "RETR Positions_Extract_%Y%m%d.csv" )

    try:
        report = []
        ftp.retrlines( cmd, lambda r: report.append( r ) )
    except ftplib.error_perm:
        # --- return empty portfolio
        return None

    mtmByBook = Structure()
    tot = 0.0

    for row in report[1:]:
        fields = row.rstrip().split( "," )

        port, book, strat = PortfolioHierarchy( fields )

        # --- skip if it doesn't match query
        if "port"  in query and not  port in  query["port"]: continue
        if "book"  in query and not  book in  query["book"]: continue
        if "strat" in query and not strat in query["strat"]: continue

        # --- skip if in skipset
        if "port"  in skip and  port in  skip["port"]: continue
        if "book"  in skip and  book in  skip["book"]: continue
        if "strat" in skip and strat in skip["strat"]: continue

        # --- read market value in fund's currency
        mtm = float( fields[12] ) if fields[12] != "" else 0.0

        # --- read end accrued items in local currency (this includes unpaid dividends)
        acc = float( fields[13] ) if fields[13] != "" else 0.0

        # --- fx local to fund currency
        fx =  1.0 / float( fields[17] )

        mtm += acc*fx
        tot += mtm

        try:
            mtmByBook[book] += mtm
        except KeyError:
            mtmByBook[book]  = mtm

    mtmByBook["Total"] = tot

    return mtmByBook
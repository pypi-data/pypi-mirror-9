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

from Agora.LIB_PortfolioFns import LeavesIterator
from Agora.LIB_PortfolioIOFns import LoadPositionsFromFile, PortNode
from Agora.LIB_DateFns import DateRange, DateRuleApply
from Agora.LIB_CurveFns import Interpolate

import sys
import os

__all__ = [ ]

################################################################################
##  attrByLongShort
##------------------------------------------------------------------------------
def attrByLongShort( sd, ed, navcrv, trades_file, rule = "+1b", fout = sys.stdout ):
    print( "date,long_mtm,short_mtm,nav", file = fout )

    for pd in DateRange( sd, ed, rule ):

        fund = LoadPositionsFromFile( trades_file, dateCutOff = pd )

        nav = Interpolate( navcrv, pd )

        long_mtm  = fund.MTM( pd, "Long" )
        short_mtm = fund.MTM( pd, "Short" )

        print( "%s,%f,%f,%f" % ( pd, long_mtm, short_mtm, nav ), file = fout )

################################################################################
##  sectorLevelAttribution
##------------------------------------------------------------------------------
def sectorLevelAttribution( sd, ed, navcrv, trades_file, aggregator,
                            sector, rule = "+1b", fout = sys.stdout ):
    print( "date,long_mtm,short_mtm,nav,long_grs,short_grs", file = fout )

    for pd in DateRange( sd, ed, rule ):
        fund = LoadPositionsFromFile( trades_file, dateCutOff = pd )
        sct  = PortNode( name = sector, nodeId = 1 )

        for leaf in LeavesIterator( fund ):
            tag = aggregator( leaf )
            if tag == sector:
                sct.addChild( leaf.clone() )

        long_mtm  = sct.MTM( pd, "Long" )
        short_mtm = sct.MTM( pd, "Short" )

        long_gross  = sct.GrossExposure( pd, "Long" )
        short_gross = sct.GrossExposure( pd, "Short" )

        nav = Interpolate( navcrv, pd )

        print( "%s,%f,%f,%f,%f,%f" % (
               pd, long_mtm, short_mtm, nav, long_gross, short_gross ), file = fout )

if __name__ == "__main__":
    from Snail.LIB_Datatypes import Date

    import Snail.CFG_FundParameters as cfg
    cfg.setup_config( cfg.__dict__, "main" )

    tradesFile = os.path.join( cfg.FUNDFOLDER, "Utilities Fund",
                               "Live Portfolio", "Archive", "PMS_LIVE.xlsm" )

    sd = Date( 2014, 1, 1 )
    ed = DateRuleApply( Date.today(), "+J-1d" )

    rule = "+b"
    usefile = False

    if usefile:
        dest = os.path.join( cfg.FUNDFOLDER, "Utilities Fund", "Live Portfolio",
                            "AlphaAnalysis", "Raw Files", "pnl_by_long_short.csv" )

        with open( dest, "w", buffering = 1 ) as fout:
            attrByLongShort( sd, ed, cfg.NAVCRV, tradesFile, rule, fout )
    else:
        attrByLongShort( sd, ed, cfg.NAVCRV, tradesFile, rule, sys.stdout )
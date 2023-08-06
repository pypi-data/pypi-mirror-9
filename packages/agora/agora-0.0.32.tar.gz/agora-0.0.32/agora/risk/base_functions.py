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

from Agora.LIB_Datatypes import Structure
from Agora.LIB_DateFns import DateRuleApply, DateRange
from Agora.LIB_CurveFns import Interpolate
from Agora.LIB_PortfolioFns import createUnique, Security, Option
from Agora.LIB_PortfolioFns import Cash, LeafNode
from Agora.CFG_FundParameters import RISKSTDT

from matplotlib import mlab

import numpy as np
import pandas
import futures

__all__ = [ ] # avoid exporting the whole namespace

# --- max number of workers used for multi-threaded blocks
MAXTHREADS = 5

################################################################################
##  ComputeRiskMetrics
##------------------------------------------------------------------------------
def ComputeRiskMetrics( portvals, ndays = 1, pctl = 95.0 ):
    if portvals is None:
        pnlloss = np.array( [ 0.0 ] )
        var     = 0.0
        cvar    = 0.0
    else:
        # --- flip the sign so that losses are positive numbers
        diffs = - ( portvals.values[ndays:,0] - portvals.values[:-ndays,0] )

        # --- for VaR and cVaR use non-overlapping differences
        pnlloss  = diffs[::ndays]
        pnlloss -= pnlloss.mean()

        var  = np.percentile( pnlloss, pctl )
        cvar = pnlloss[ pnlloss > var ].mean()

    return { "Std"  : pnlloss.std(),
             "VaR"  : var,
             "cVaR" : cvar }

################################################################################
##  ComputeWorstLosses
##------------------------------------------------------------------------------
def ComputeWorstLoss( portvals, ndays = 1 ):
    if portvals is None:
        maxloss   = 0.0
        maxlossDt = None
    else:
        # --- flip the sign so that losses are positive numbers
        diffs = - ( portvals.values[ndays:,0] - portvals.values[:-ndays,0] )

        # --- for max loss, consider all (i.e. overlapping) ndays-differences
        dates   = portvals.index[:-ndays]
        maxloss = diffs.max()

        maxlossIdx = mlab.find( diffs == maxloss )
        maxlossDt  = dates[maxlossIdx].item( 0 ).strftime( "%d-%b-%Y" )

    return { "MaxLoss"   : maxloss,
             "MaxLossDt" : maxlossDt }

################################################################################
##  NodeVaR
##------------------------------------------------------------------------------
def NodeVaR( node, mdd, sd, ed ):
    if isinstance( node, LeafNode ):
        if node.qty == 0.0:
            return None
        results = { "isLeaf" : True  }

    else:
        if len( node.positions ) == 0:
            return None
        results = { "loaded" : True  }

    portvals = node.PortfolioValues( mdd, RISKSTDT, ed )
    varvalues = portvals.truncate( before = sd )

    dailyRisks95 = ComputeRiskMetrics( varvalues, pctl = 95.0 )
    dailyRisks99 = ComputeRiskMetrics( varvalues, pctl = 99.0 )
    dailyMaxLoss = ComputeWorstLoss( portvals )

    # --- recursively determine hierarchy level
    level = 0
    this  = node
    while this.parent is not None:
        level += 1
        this   = this.parent

    results.update( {
            "id"           : node.nodeid,
            "name"         : node.name,
            "level"        : level,
            "expanded"     : level <= 1,
            "parent"       : None if node.parent is None else node.parent.nodeid,
            "gross"        : node.GrossExposure( mdd ),
            "net"          : node.NetExposure( mdd ),
            "dailyStd"     : dailyRisks95["Std"],
            "dailyVaR95"   : dailyRisks95["VaR"],
            "dailyVaR99"   : dailyRisks99["VaR"],
            "dailycVaR95"  : dailyRisks95["cVaR"],
            "dailyMaxLoss" : dailyMaxLoss["MaxLoss"],
        } )

    return results

################################################################################
##  VaRTree
##------------------------------------------------------------------------------
def VaRTree( fund, mdd, sd, ed, skipCcy = False ):

    tree = [ NodeVaR( fund, mdd, sd, ed ) ]

    for port in fund.children.itervalues():
        if skipCcy and all( [ sec.isccy for sec in port.positions.iterkeys() ] ):
            continue

        tree.append( NodeVaR( port, mdd, sd, ed ) )

        for book in port.children.itervalues():
            if skipCcy and all( [ sec.isccy for sec in book.positions.iterkeys() ] ):
                continue

            tree.append( NodeVaR( book, mdd, sd, ed ) )

            for strat in book.children.itervalues():
                if skipCcy and all( [ sec.isccy for sec in strat.positions.iterkeys() ] ):
                    continue

                tree.append( NodeVaR( strat, mdd, sd, ed ) )

                for pos in strat.children.itervalues():
                    if skipCcy and all( [ sec.isccy for sec in pos.positions.iterkeys() ] ):
                        continue

                    tree.append( NodeVaR( pos, mdd, sd, ed ) )

    return [ item for item in tree if item is not None ]

################################################################################
##  ComputeBetas
##------------------------------------------------------------------------------
def ComputeBetas( positions, index, mdd, sd, ed, aum ):
    # --- early return for empty portfolio
    if len( positions ) == 0:
        return {}, 0.0

    # --- load index prices
    index_prcs = index.historicalPrices( sd, ed )

    betasBySec = {}
    totalBeta = 0.0

    for sec, qty in positions.iteritems():
        # --- skip currency positions
        if sec.isccy:
            continue

        if isinstance( sec, Option ):
            qty *= sec.delta( mdd )
            prcs = sec.histUdlPrices( sd, ed )
            last = sec.underlying.lastAdjUSD( mdd )

        else:
            prcs = sec.historicalPrices( sd, ed )
            last = sec.lastAdjUSD( mdd )

        if sec == index:
            beta = 1.0
        else:
            combo = pandas.concat( [ index_prcs, prcs ], axis = 1 ).dropna()
            rets = np.diff( np.log( combo.values ), axis = 0 )
            x, y = rets[:,0], rets[:,1]
            beta, alpha = np.linalg.lstsq( np.vstack( [ x, np.ones_like( x ) ] ).T, y )[0]

        totalBeta += beta*qty*last
        betasBySec[sec.name] = beta

    return betasBySec, totalBeta / aum

################################################################################
##  ComputeExposures
##------------------------------------------------------------------------------
def ComputeExposures( positions, mdd ):

    def getExposureInfo( ( sec, qty ) ):
        if sec.ccy == "GBp":
            ccy, scale = "GBP", 0.01
        else:
            ccy, scale = sec.ccy, 1.0

        if isinstance( sec, Cash ):
            lastUsd = sec.lastUSD( mdd )

            return ccy, qty*np.array( [ scale, lastUsd ] )

        else:
            if sec.isccy:
                last = sec.last( mdd )
                ccy  = sec.base

                return ccy, qty*np.array( [ 1.0, last ] )

            else:
                # --- for ADRs the real exposure is to the currency of the
                #     underlying shares
                if sec.ccy != sec.undlccy:
                    lastUsd = sec.lastUSD( mdd )
                    last    = lastUsd / sec.adrcross.last( mdd )
                    ccy, scale = sec.undlccy, 1.0
                else:
                    last    = sec.last( mdd )
                    lastUsd = sec.lastUSD( mdd )

                return ccy, qty*np.array( [ scale*last, lastUsd ] )

    with futures.ThreadPoolExecutor( max_workers = MAXTHREADS ) as exe:
        exposureInfo = list( exe.map( getExposureInfo, positions.iteritems() ) )

    exposure = Structure()

    for ccy, thisExposure in exposureInfo:
        exposure[ccy] = exposure.get( ccy, 0.0 ) + thisExposure

    return exposure

################################################################################
##  RunHistorical
##------------------------------------------------------------------------------
def RunHistorical( loader, sd, ed, navcrv, verbose = True ):

    dates, values = [], []

    index = createUnique( "SX5E Index", "EUR", Security )

    for pd in DateRange( sd, ed, "+1b" ):
        risk_ed = DateRuleApply( pd, "-1b" )
        risk_sd = DateRuleApply( pd, "-1b-60m" )
        beta_ed = DateRuleApply( pd, "-1b" )
        beta_sd = DateRuleApply( pd, "-1b-12m" )

        fund = loader( pd )

        nav = Interpolate( navcrv, pd )
        mtm = 0.0#fund.MTM( pd )

        risk = NodeVaR( fund, pd, risk_sd, risk_ed )

        _, beta = ComputeBetas( fund.positions, index, pd, beta_sd, beta_ed, nav )

        grsexp  = fund.GrossExposure( pd )
        netexp  = fund.NetExposure( pd )

        vls = [ mtm,
                0.0 if risk is None else risk["dailyVaR95"],
                0.0 if risk is None else risk["dailyVaR99"],
                0.0 if risk is None else risk["dailycVaR95"],
                0.0 if risk is None else risk["dailyMaxLoss"],
                0.0 if risk is None else risk["dailyStd"],
                grsexp, netexp, beta ]

        dates.append( pd )
        values.append( vls )

        if verbose:
            print pd, vls

    return pandas.DataFrame( data = values, index = dates,
                             columns = [ "MtM", "VaR95", "VaR99", "cVaR95",
                                         "MaxLoss", "Std", "GrossExp", "NetExp", "TotBeta" ] )

################################################################################
##  RunHistoricalDetailed
##------------------------------------------------------------------------------
def RunHistoricalDetailed( loader, fundname, navcrv, dates, strats ):

    index = createUnique( "SX5E Index", "EUR", Security )

    colnames = [ "%sMTM" % s.replace( " ", "" ) for s in strats ] + \
               [ "LongMtm", "ShortMTM", "FundMtM" ] + \
               [ "%sGrsExp" % s.replace( " ", "" ) for s in strats ] + \
               [ "FundGrsExp" ] + \
               [ "%sNetExp" % s.replace( " ", "" ) for s in strats ] + \
               [ "NetExp", "Beta", "VaR95", "VaR99", "Std", "AUM" ]

    values = []

    for pd in dates:

        fund = loader( pd )
        port = fund.children[fundname]

        risk_ed = DateRuleApply( pd, "-1b" )
        risk_sd = DateRuleApply( pd, "-1b-60m" )
        beta_ed = DateRuleApply( pd, "-1b" )
        beta_sd = DateRuleApply( pd, "-1b-12m" )

        nav = Interpolate( navcrv, pd )

        fund_mtm  = port.MTM( pd )
        long_mtm  = port.MTM( pd, longShort = "Long" )
        short_mtm = port.MTM( pd, longShort = "Short" )

        strats_mtm = [ port.children[strt].MTM( pd )
                       if strt in port.children else 0.0 for strt in strats ]

        _, beta = ComputeBetas( port.positions, index, pd, beta_sd, beta_ed, nav )

        grsexp = port.GrossExposure( pd )
        netexp = port.NetExposure( pd )

        strats_grsexp = []
        strats_netexp = []
        for strt in strats:
            if strt in port.children:
                ge = port.children[strt].GrossExposure( pd )
                ne = port.children[strt].NetExposure( pd )
            else:
                ge = 0.0
                ne = 0.0
            strats_grsexp.append( ge )
            strats_netexp.append( ne )

        risk = NodeVaR( port, pd, risk_sd, risk_ed )

        vls = strats_mtm + \
              [ long_mtm, short_mtm, fund_mtm ] + \
              strats_grsexp + \
              [ grsexp ] + \
              strats_netexp + \
              [ netexp, beta, risk["dailyVaR95"], risk["dailyVaR99"], risk["dailyStd"], nav ]

        values.append( vls )

        print pd, vls

    return pandas.DataFrame( data = values, index = dates, columns = colnames )


if __name__ == "__main__":
    from Snail.LIB_Datatypes import Date
    from Snail.LIB_PortfolioIOFns import LoadPositionsFromFtp
    from pylab import *

    def loader( mdd ):
        return LoadPositionsFromFtp( "ftp.cf-partners.com","paladyne",
                                     "lK$b6JVJ", mdd, "CFP Equity Master Fund Limited" )

    def pnl_histogram( mdd ):
        fund = loader( mdd  )
        sd = DateRuleApply( mdd, "-1b-60m" )
        ed = DateRuleApply( mdd, "-1b" )
        portvals = fund.PortfolioValues( mdd, sd, ed )
        diffs = - ( portvals.values[1:,0] - portvals.values[:-1,0] )
        hist( diffs, 100 )

    pnl_histogram( Date.today() )

    show()
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

from Agora.LIB_PortfolioFns import Option
from Agora.LIB_FinancialFramework import Scenario
from Agora.LIB_Commod_EquityModels import Company
from Agora.LIB_Commod_Definitions import *

from collections import namedtuple

EPSILON = 0.10
SHOCKS  = [
    ( EPSILON, (  api2,      "spot",     api2.spot*( 1.0 + EPSILON ) ) ),
    ( EPSILON, (   eua,      "spot",      eua.spot*( 1.0 + EPSILON ) ) ),
    ( EPSILON, (   ttf,      "spot",      ttf.spot*( 1.0 + EPSILON ) ) ),
    ( EPSILON, (   nbp,      "spot",      nbp.spot*( 1.0 + EPSILON ) ) ),
    ( EPSILON, ( cepwr,    "spread",  cepwr.spread*( 1.0 + EPSILON ) ) ),
    ( EPSILON, ( ukpwr,    "spread",  ukpwr.spread*( 1.0 + EPSILON ) ) ),
    ( EPSILON, ( brent,      "spot",    brent.spot*( 1.0 + EPSILON ) ) ),
    ( EPSILON, (   eur, "usd_cross", eur.usd_cross*( 1.0 + EPSILON ) ) ),
    ( EPSILON, (   gbp, "usd_cross", gbp.usd_cross*( 1.0 + EPSILON ) ) ),
]

CommodExp = namedtuple( "CommodExp",
                        [ "API2", "EUA", "TTF", "NBP",
                          "CE_CDS", "UK_CSS", "Oil", "EURUSD", "GBPUSD" ] )

################################################################################
##  ParsePortfolio
##------------------------------------------------------------------------------
def ParsePortfolio( pd, fund, nav ):
    port = {}
    for sec, qty in fund.positions.iteritems():
        if isinstance( sec, Option ):
            # --- load current price in dollars for the underlyier
            prc = sec.underlying.lastUSD( pd )
            pos = sec.delta( pd )*qty*prc
            key = sec.underlying.name
        else:
            # --- load current price in dollars
            prc = sec.lastUSD( pd )
            pos = qty*prc
            key = sec.name

        port[key] = port.get( key, 0.0 ) + pos / nav

    return port

################################################################################
##  GetSensitivities
##------------------------------------------------------------------------------
def GetSensitivities( models, shocks ):
    exposures = {}
    for name, model in sorted( models.iteritems() ):
        if isinstance( model, Company ):
            base = model.net_income
        else:
            base = model.spot

        deltas = []
        for eps, shock in shocks:
            with Scenario( [ shock ] ):
                if isinstance( model, Company ):
                    shocked = model.net_income
                    delta   = ( shocked - base ) / model.total_net_income / eps
                else:
                    shocked = model.spot
                    delta   = ( shocked / base - 1.0 ) / eps

            deltas.append( delta )

        exposures[name] = CommodExp( *deltas )

    return exposures

################################################################################
##  printSensitivities
##------------------------------------------------------------------------------
def printSensitivities( sensitivities ):

    fmt = "%20s %9s %9s %9s %9s %9s %9s %9s %9s %9s"

    print fmt % ( "Company", "API2", "EUA", "TTF", "NBP", "CE-CDS", "UK-CSS", "Oil", "EURUSD", "GBPUSD" )
    print fmt % ( "-"*20, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8 )

    for name, sensitivity in sorted( sensitivities.iteritems() ):
        print "%20s " % name,
        for delta in sensitivity:
            print "%7.1f%% " % ( delta*100.0 ),
        print ""

################################################################################
##  printExposures
##------------------------------------------------------------------------------
def printExposures( port, sensitivities, shocks ):
    fmt = "%20s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s"

    print fmt % ( "Company", "Weight", "API2", "EUA", "TTF", "NBP", "CE-CDS", "UK-CSS", "Oil", "EURUSD", "GBPUSD" )
    print fmt % ( "-"*20, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8 )

    total_exp = CommodExp( *[ 0.0 ]*len( shocks ) )
    for sec, weight in sorted( port.iteritems() ):

        try:
            this_exp  = CommodExp( *[ weight*e for e in sensitivities[sec] ] )
            total_exp = CommodExp( *[ x+y for x,y in zip( total_exp, this_exp ) ] )

            print "%20s  %7.1f%% " % ( sec, weight*100.0 ),
            for delta in this_exp:
                print "%7.1f%% " % ( delta*100.0 ),
            print ""

        except KeyError:
            continue

    print fmt % ( "-"*20, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8, "-"*8 )
    print "%20s %9s " % ( "Portfolio", "" ),
    for delta in total_exp:
        print "%7.1f%% " % ( delta*100.0 ),
    print ""

################################################################################
##  ExposuresAsJson
##------------------------------------------------------------------------------
def ExposuresAsJson( port, sensitivities, shocks ):
    table = {
        "header": ( "Security", "Weight", "API2", "EUA", "TTF",
                    "NBP", "CE-CDS", "UK-CSS", "Oil", "EURUSD", "GBPUSD" ),
        "rows": [],
    }

    total_exp = CommodExp( *[ 0.0 ]*len( shocks ) )
    for sec, weight in sorted( port.iteritems() ):

        record = []
        try:
            this_exp  = CommodExp( *[ weight*e for e in sensitivities[sec] ] )
            total_exp = CommodExp( *[ x+y for x,y in zip( total_exp, this_exp ) ] )

            record.append( sec )
            record.append( weight*100.0 )

            for delta in this_exp:
                record.append( delta*100.0 )

            table["rows"].append( record )

        except KeyError:
            continue

    record = [ "Portfolio", "" ]
    for delta in total_exp:
        record.append( delta*100.0 )
    table["total"] = record

    return table

##------------------------------------------------------------------------------
if __name__ == "__main__":
    from Snail.LIB_Commod_EquityDefinitions import COMPANY_MODELS
    from Snail.LIB_CurveFns import Interpolate
    from Snail.CFG_FundParameters import NAVCRV

    from Snail.LIB_PortfolioIOFns import LoadPositionsFromFtp
    from Snail.CFG_FundParameters import FTPHOST, FTPUSER, FTPPASSWD

    pd = Date.today()

    fund = LoadPositionsFromFtp( FTPHOST, FTPUSER, FTPPASSWD, pd,
                                 query = { "port": { "CFP Equity Master Fund Limited" } } )

#    printSensitivities( GetSensitivities( COMPANY_MODELS, SHOCKS ) )

    securities = ParsePortfolio( pd, LoadPortfolio( pd ), Interpolate( NAVCRV, pd ) )
    print ExposuresAsHtml( securities, GetSensitivities( COMPANY_MODELS, SHOCKS ), SHOCKS )

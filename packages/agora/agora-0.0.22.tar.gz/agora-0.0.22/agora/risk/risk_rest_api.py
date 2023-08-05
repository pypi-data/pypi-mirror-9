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

from Abacus.Datatypes.Date import Date
from Agora.LIB_CurveFns import Interpolate
from Agora.LIB_DateFns import DateRuleApply
from Agora.LIB_BloombergAPI import BloombergError
from Agora.LIB_BloombergDataServer import BbgDataClient
from Agora.LIB_PortfolioFns import createUnique, Security, Option, PortNode, LeafNode, FLOATING
from Agora.LIB_PortfolioIOFns import LoadPositionsFromFtp
from Agora.LIB_Risk_BaseFns import NodeVaR, ComputeBetas, RunHistorical
from Agora.LIB_Risk_PnLFns import LoadMtMFromFtp
from Agora.LIB_ConfigFns import loadConfig
from Agora.CFG_FundParameters import FTPHOST, FTPUSER, FTPPASSWD

from LIB_RiskServer import monitorDailyVaR, monitorNetExposure, monitorGrossExposure, \
                           monitorSingleNameExposure, monitorSingleNameLiquidity, monitorOwnership

from functools import partial

import zmq.eventloop.ioloop as zmq_ioloop
import zmq.eventloop.zmqstream as zmq_stream
import zmq

import pkg_resources
import datetime
import traceback
import cPickle
import json
import logging
import argh
import user
import math

logging.basicConfig(
    level = logging.DEBUG,
    format = "%(asctime)-15s %(levelname)-8s %(name)-32s %(message)s"
)
logger = logging.getLogger(__name__)

# --- bloomberg data client
bbgClient = BbgDataClient()

V95, V99, CV95, ML = "dailyVaR95", "dailyVaR99", "dailycVaR95", "dailyMaxLoss"

RR_HEAD = """
<tr>
    <th style='width:110px;'>VaR95</th>
    <th style='width:110px;'>VaR99</th>
    <th style='width:110px;'>cVaR95</th>
    <th style='width:110px;'>MaxLoss</th>
    <th style='width:110px;'>Std</th>
    <th style='width:110px;'>GrossExp</th>
    <th style='width:110px;'>NetExp</th>
    <th style='width:110px;'>TotBeta</th>
</tr>
"""

RR_BODY = """
<tr>
    <th style='width:110px;'>{0:6.3f}</th>
    <th style='width:110px;'>{1:6.3f}</th>
    <th style='width:110px;'>{2:6.3f}</th>
    <th style='width:110px;'>{3:6.3f}</th>
    <th style='width:110px;'>{4:6.3f}</th>
    <th style='width:110px;'>{5:6.3f}</th>
    <th style='width:110px;'>{6:6.3f}</th>
    <th style='width:110px;'>{7:6.3f}</th>
</tr>
"""

RR_FIELDS = [ "VaR95", "VaR99", "cVaR95", "MaxLoss", "Std", "GrossExp", "NetExp" ]

################################################################################
##  ReportError
##------------------------------------------------------------------------------
class ReportError( Exception ):
    pass

################################################################################
##  OnDemandServer
##------------------------------------------------------------------------------
class OnDemandServer( object ):
    ############################################################################
    ##  Initialization
    ##--------------------------------------------------------------------------
    def __init__( self, pd, url ):
        # --- positions file timestamp
        self.timestamp = None

        self.context = zmq.Context()
        self.socket = self.context.socket( zmq.REP )
        self.socket.bind( url )

        # --- tornado event-loop
        self.loop = zmq_ioloop.IOLoop.instance()
        self.stream = zmq_stream.ZMQStream( self.socket, self.loop )

        self.index = createUnique( "SX5E Index", "EUR", Security )

        self.pd = pd
        self.risk_ed = DateRuleApply( self.pd, "-1b" ).date()
        self.risk_sd = DateRuleApply( self.pd, "-1b-60m" ).date()
        self.beta_ed = DateRuleApply( self.pd, "-1b" ).date()
        self.beta_sd = DateRuleApply( self.pd, "-1b-12m" ).date()

    ############################################################################
    ##  loader
    ##--------------------------------------------------------------------------
    def loader( self, pd ):
        return LoadPositionsFromFtp( FTPHOST, FTPUSER, FTPPASSWD, pd,
                                     query = { "port": { self.cfg["FUNDNAME"] } } )

    ############################################################################
    ##  genRiskReport
    ##--------------------------------------------------------------------------
    def genRiskReport( self, parms ):
        # --- load configuration for specific fund
        self.cfg = loadConfig( parms["fund"] )
        navcrv = self.cfg["NAVCRV"]

        # --- error checking
        if parms["sd"] == "":
            raise ReportError( "Start Date has not been selected" )
        if parms["ed"] == "":
            raise ReportError( "End Date has not been selected" )

        sd = Date.parse( parms["sd"] )
        ed = Date.parse( parms["ed"] )

        if ed < sd:
            raise ReportError( "Selected start and end "
                               "dates are inconsistent: Start Date > End Date" )

        if sd < DateRuleApply( ed, "-30d" ):
            raise ReportError( "This report can AT MOST "
                               "retrive 30 days of data at the time" )

        data = RunHistorical( self.loader, sd, ed, navcrv, verbose = False )

        report  = "<br><table>"
        report += "<thead><tr>"
        report += "<th style='width:80px;'>Date</th>"
        report += "<th style='width:95px;'>LtD Gross P&L</th>"
        report += "<th style='width:80px;'>VaR P95</th>"
        report += "<th style='width:80px;'>VaR P99</th>"
        report += "<th style='width:80px;'>cVaR P95</th>"
        report += "<th style='width:80px;'>Max.Loss</th>"
        report += "<th style='width:80px;'>Std</th>"
        report += "<th style='width:90px;'>Gross Exp.</th>"
        report += "<th style='width:80px;'>Net Exp.</th>"
        report += "<th style='width:55px;'>Beta</th>"
        report += "<th style='width:85px;'>AUM</th>"
        report += "</tr></thead>"
        report += "<tbody>"

        for d in data.index:
            aum = Interpolate( navcrv, d )
            mtm = LoadMtMFromFtp( FTPHOST, FTPUSER, FTPPASSWD, date = d,
                                  query = { "port": { self.cfg["FUNDNAME"] } },
                                  skip = { "strat": { "Subscriptions and Redemptions",
                                                      "Performance Fees",
                                                      "Management Fees" } } )

            report += "<tr>" + \
                      d.strftime( "<td>%d-%b-%Y</td>" ) + \
                      "<td>%.2f</td>" % mtm["Total"] + \
                      "".join( [ "<td>%.1f</td>" % data[field][d] for field in RR_FIELDS ] ) + \
                      "<td>%.4f</td>" % data["TotBeta"][d] + \
                      "<td>%.1f</td>" % aum + \
                      "</tr>"

        report += "</tbody>"
        report += "</table><br>"

        return report

    ############################################################################
    ##  genWhatIfReport
    ##--------------------------------------------------------------------------
    def genWhatIfReport( self, parms ):
        # --- load configuration for specific fund
        self.cfg = loadConfig( parms["fund"] )
        aum = Interpolate( self.cfg["NAVCRV"], self.pd )

        fund = self.loader( self.pd )

        aggregated = fund.clone()
        newTrades  = aggregated.addChild( PortNode( name = "New Trades" ) )

        avg_volumes = {}
        for pos in parms["trades"]:
            # --- read security and quantity, skip if security is not set
            sec = str( pos["security"] ).strip().upper()
            if sec == "":
                continue

            qty = float( pos["quantity"] )

            # --- load currency and futures lot size from bloomberg
            try:
                ccy = bbgClient.BDP( sec, "CRNCY" )
            except BloombergError:
                raise BloombergError( "Couldn't find security <em>%s</em>: "
                                      "make sure the ticker is spelled correctly" % sec )

            # --- determine security type
            try:
                sectype = bbgClient.BDP( sec, "SECURITY_TYP2" )
            except BloombergError:
                raise BloombergError( "Unrecognized security type for <em>%s</em>" % sec )

            # --- create security based on security type
            if sectype in { "Common Stock", "Depositary Receipt", "Right", "Preference", "Future" }:
                sec = createUnique( sec, ccy, Security )
            elif sectype in { "Option" }:
                sec = createUnique( sec, ccy, Option )
            else:
                raise ValueError( "Unrecognized security "
                                  "type for <em>%s</em>: %s" % ( sec, sectype ) )

            fcs = sec.cntSize
            avg_volumes[sec.name] = sec.avgVolume

            # --- append position to portfolio
            newTrades.addChild( LeafNode( sec.name, ccy, qty*fcs,
                                          sectype = FLOATING,
                                          longShort = "Long" if qty > 0.0 else "Short" ) )

        report = {
            "positions": {},
            "risks": {
                "metrics": ( "VaR(P95)", "VaR(P99)", "cVaR(P95)", "Max. Loss",
                             "Net Exposure", "Gross Exposure", "Portfolio's Beta" ),
                "levels": ( "Current Portfolio", "New Positions", "New Portfolio" ),
                "rows": {},
            },
        }
        levels = dict( zip( report["risks"]["levels"], ( fund, newTrades, aggregated ) ) )

        for level, port in levels.iteritems():

            _, beta = ComputeBetas( port.positions, self.index, self.pd, self.beta_sd, self.beta_ed, aum )
            net = port.NetExposure( self.pd )
            grs = port.GrossExposure( self.pd )
            rsk = NodeVaR( port, self.pd, self.risk_sd, self.risk_ed )

            if rsk is None:
                rsk = { V95: 0.0, V99: 0.0, CV95: 0.0, ML: 0.0 }

            report["risks"]["rows"][level] = {
                "VaR(P95)": { "value": 100.0*rsk[V95] / aum, "color": monitorDailyVaR( rsk[V95] / aum ) },
                "VaR(P99)": { "value": 100.0*rsk[V99] / aum, "color": "plain" },
                "cVaR(P95)": { "value": 100.0*rsk[CV95] / aum, "color": "plain" },
                "Max. Loss": { "value": 100.0*rsk[ML] / aum, "color": "plain" },
                "Net Exposure": { "value": 100.0*net / aum, "color": monitorNetExposure( net / aum ) },
                "Gross Exposure": { "value": 100.0*grs / aum, "color": monitorGrossExposure( grs / aum ) },
                "Portfolio's Beta": { "value": beta, "color": "plain" },
            }

        for sec, qty in aggregated.positions.iteritems():
            if not sec.name in avg_volumes:
                continue

            prc = sec.underlying.lastUSD( self.pd )
            exposure = qty*prc*sec.delta( self.pd )
            weight = 100.0 * exposure / aum

            # --- ownership as percentage of mkt cap
            if sec.name.endswith( "INDEX" ) or sec.name.endswith( "COMDTY" ):
                ownership = 0.0
                pct_of_max_vol = 0.0
            else:
                ownership = 100.0 * exposure / sec.mktCap( self.pd )
                pct_of_max_vol = 100.0 * math.fabs( qty ) / ( 3.0*avg_volumes[sec.name] )

            report["positions"][sec.name] = {
                "exposure": exposure,
                "position": qty / sec.cntSize,
                "weight": weight,
                "pctOfMaxVolume": pct_of_max_vol,
                "beta": 0.0,
                "ownership": ownership,
                "exchange": sec.underlying.undlexch,
                # --- color codes for monitored fields
                "weightColor": monitorSingleNameExposure( weight ),
                "pctOfMaxVolumeColor": monitorSingleNameLiquidity( pct_of_max_vol ),
                "ownershipColor": monitorOwnership( ownership, sec.underlying.undlexch ),
            }

        return json.dumps( report )

    ############################################################################
    ##  processRequest
    ##--------------------------------------------------------------------------
    def processRequest( self, request ):
        try:
            address, request = cPickle.loads( request[0] )

            logger.info( "processing request from %s" % address )

            if request["report"] == "What-If":
                logger.info( "generating What-If analysis" )
                report = self.genWhatIfReport( request["parms"] )

            elif request["report"] == "Risk-Report":
                logger.info( "generating on-demand Risk Report" )
                report = self.genRiskReport( request["parms"] )

            else:
                raise RuntimeError( "unrecognized report: %s" % request["report"] )

            logger.info( "sending report to %s" % address )
            self.stream.send_string( report )
            logger.info( "report sent successefully" )

        except ( ReportError, BloombergError ) as err:
            # --- send exception text back to caller
            self.stream.send_string( json.dumps( {
                "error": "<br><p style='text-align:center'>ERROR: %s</p><br>" % err } ) )
            logger.critical( "failed to generate report", exc_info = True  )

        except:
            # --- send full traceback back to caller
            self.stream.send_string( json.dumps( {
                "error": "ERROR: " + traceback.format_exc( 8 ) } ) )
            logger.critical( "failed to generate report", exc_info = True )

    ############################################################################
    ##  checkStop
    ##--------------------------------------------------------------------------
    def checkStop( self, stopAt ):
        if datetime.datetime.now() > stopAt:
            self.loop.stop()

    ############################################################################
    ##  start
    ##--------------------------------------------------------------------------
    def start( self, stopAt ):
        logger.info( "Starting On-Demand Server: Version is %s, Pricing Date is %s" % (
                     pkg_resources.require( "Snail" )[0].version, self.pd ) )

        # --- register a callback to check if need to stop the server
        zmq_ioloop.PeriodicCallback( partial( self.checkStop, stopAt ),
                                     callback_time = 15000, io_loop = self.loop ).start()

        self.stream.on_recv( self.processRequest )
        self.loop.start()

        logging.info( "Stopped On-Demand Server" )

################################################################################
##  run
##------------------------------------------------------------------------------
def run( port = 5000 ):
    pd = Date.today()

    # --- stop server just before midnight
    bizday   = DateRuleApply( pd, "+1b-1d" )
    stopTime = datetime.datetime.combine( bizday, datetime.time( 23, 59, 59 ) )

    server = OnDemandServer( pd = pd, url = "%s:%d" % ( "tcp://127.0.0.1", port ) )
    server.start( stopAt = stopTime )

################################################################################
##  main
##------------------------------------------------------------------------------
def main():
    argh.dispatch_command( run, namespace = user )

if __name__ == "__main__":
    run()
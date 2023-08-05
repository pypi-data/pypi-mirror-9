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

from Agora.LIB_Datatypes import Date
from Agora.LIB_DateFns  import DateRuleApply, CountBizDays
from Agora.LIB_BloombergAPI import BloombergError
from Agora.LIB_PortfolioIOFns import LoadPositionsFromFtp
from Agora.LIB_Datatypes import Structure
from Agora.LIB_Risk_BaseFns import VaRTree, ComputeRiskMetrics, \
                                   ComputeWorstLoss, ComputeBetas, ComputeExposures
from Agora.LIB_Risk_StressTests import StressTestReport

from Agora.LIB_Commod_EquityDefinitions import COMPANY_MODELS
from Agora.LIB_Risk_CommodSensitivities import ParsePortfolio, GetSensitivities, \
                                               ExposuresAsJson, SHOCKS

from Agora.LIB_RiskServer import monitorSingleNameExposure, monitorSingleNameLiquidity, \
                                 monitorOwnership, monitorNetExposure, monitorGrossExposure, \
                                 monitorCommodExposure, monitorDailyVaR, monitorDaysToExpiration

from Agora.CFG_FundParameters import FTPHOST, FTPUSER, FTPPASSWD
from Agora.CFG_FundParameters import STRESS_TEST_SCENARIOS, RISKSTDT

from dateutil.relativedelta import relativedelta

import dateutil.parser
import pkg_resources
import urllib2
import time
import math
import ftplib
import json
import futures
import logging
import argh
import user
import urllib
import pymongo

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)-15s %(levelname)-8s %(name)-32s %(message)s"
)
logger = logging.getLogger( __name__ )

# --- max number of workers used for multi-threaded blocks
MAXTHREADS = 10

# --- settings for risk metrics
RISK_HORIZONS = ( (   "Daily",  1 ),
                  (  "Weekly",  5 ),
                  ( "Monthly", 21 ) )

RISK_METRICS = ( (  "%s VaR (P95)", "VaR95", [] ),
                 (  "%s VaR (P99)", "VaR99", [ "Weekly", "Monthly" ] ),
                 ( "%s cVaR (P95)", "cVaR95", [] ),
                 (   "Max %s Loss", "MaxLoss", [] ) )

################################################################################
##  RiskServer
##------------------------------------------------------------------------------
class RiskServer( object ):
    ############################################################################
    ##  Initialization
    ##--------------------------------------------------------------------------
    def __init__( self, pd, url, fundname, portfolio, aum, indexes,
                  mongodb_uri, resend_freq = 10, recalc_freq = 60, archive = False ):
        # --- pricing date used to calculate reports
        self.pd = pd

        # --- web server url
        self.url = url

        # --- tag used to identify the fund
        self.fundname = fundname

        # --- only load positions for selected portfolio
        self.portfolio = portfolio

        # --- assets under mamagement
        self.aum = aum

        # --- indexes used for beta
        self.indexes = indexes

        # --- resend reports interval (in seconds)
        self.resend_freq = resend_freq

        # --- recalc reports interval (in seconds)
        self.recalc_freq = recalc_freq
        self.t0 = Date.now()

        # --- should we archive reports in mongodb?
        self.archive = archive

        # --- positions file timestamp
        self.timestamp = None

        self.pvdt = DateRuleApply( self.pd, "-1b" )
        self.risk_ed = DateRuleApply( self.pd, "-1b" )
        self.risk_sd = DateRuleApply( self.pd, "-1b-60m" )
        self.beta_ed = DateRuleApply( self.pd, "-1b" )
        self.beta_sd = DateRuleApply( self.pd, "-1b-12m" )

        self.fund = None
        self.reports = Structure()
        self.positions = {}
        self.currencies = []

        self.commod_sensitivities = GetSensitivities( COMPANY_MODELS, SHOCKS )

        self.db_conn = pymongo.MongoClient( mongodb_uri ).get_default_database()
        self.db_coll = self.db_conn["snail"]["RiskServer"]

    ############################################################################
    ##  parsePositions
    ##--------------------------------------------------------------------------
    def parsePositions( self ):
        """
        Parse trades file and returns True if positions have changed.
        """
        # --- first check if time stamp on the file has changed
        try:
            ftp = ftplib.FTP( FTPHOST, FTPUSER, FTPPASSWD, timeout = 2 )
            tstmp = ftp.sendcmd( self.pd.strftime( "MDTM Positions_Extract_%Y%m%d.csv" ) )
            ftp.close()

            if tstmp[:3] == "213":
                tstmp = dateutil.parser.parse( tstmp[3:].strip() )
            else:
                tstmp = None

            if self.timestamp is not None and self.timestamp == tstmp:
                return False
            else:
                self.timestamp = tstmp

            logger.info( "parsing positions from {0}"
                         "as of date {1}".format( FTPHOST, self.pd ) )
            fund = LoadPositionsFromFtp( FTPHOST, FTPUSER, FTPPASSWD,
                                         date = self.pd,
                                         query = { "port": { self.portfolio } } )
            logger.info( "done loading positions" )

        except:
            logger.exception( "failed to parse positions" )
            return False

        # --- update if needed and return status
        if self.fund is None or fund != self.fund:
            self.fund = fund
            return True
        else:
            return False

    ############################################################################
    ##  addFundInfo
    ##--------------------------------------------------------------------------
    def addFundInfo( self, timestamp ):
        t0 = Date.now()
        logger.info( "adding fund's info" )

        data = {
            "timestamp": timestamp,
            "aum": self.aum,
            "pd": self.pd.strftime( "%d-%b-%y" ),
            "fund": self.portfolio,
        }

        self.reports["INFO"] = {
            "fund": self.fundname,
            "topic": "INFO",
            "report": json.dumps( data, sort_keys = True ) }

        logger.info( "done in %s", ( Date.now() - t0 ) )

    ############################################################################
    ##  addPosAndBetas
    ##--------------------------------------------------------------------------
    def addPosAndBetas( self, timestamp ):
        t0 = Date.now()
        logger.info( "adding pos and betas" )

        #-----------------------------------------------------------------------
        #   positions and betas
        #-----------------------------------------------------------------------
        # --- compute betas to the reference index
        betas, port_beta = ComputeBetas( self.fund.positions, self.indexes[0],
                                         self.pd, self.beta_sd, self.beta_ed, self.aum )

        logger.info( "ComputeBetas took %s", ( Date.now() - t0 ) )

        net_exposure = 0.0
        grs_exposure = 0.0
        com_exposure = 0.0
        positions_table = {}

        for sec, qty in self.fund.positions.iteritems():
            # --- skip currency positions
            if sec.isccy: continue

            # --- price and position in USD
            prc = sec.underlying.lastUSD( self.pd )
            exposure = qty*prc*sec.delta( self.pd )

            # --- cache position expressed as dollar exposure
            self.positions[sec.name] = exposure

            # --- get beta for this security
            beta = betas[sec.name]

            # --- get bloomberg raw-beta on the natural index
            try:
                bbg_beta = sec.bbg.BDP( sec.underlying.name, "EQY_RAW_BETA" )
            except BloombergError:
                bbg_beta = None

            # --- get position's weight as % of AUM
            weight = 100.0 * exposure / self.aum

            # --- ownership as percentage of mkt cap
            if sec.name.endswith( "INDEX" ) or sec.name.endswith( "COMDTY" ):
                ownership = 0.0
                pct_of_max_vol = 0.0
            else:
                ownership = 100.0 * exposure / sec.mktCap( self.pd )
                pct_of_max_vol = 100.0 * math.fabs( qty ) / ( 3.0*sec.avgVolume )

            # --- last tradable date
            try:
                expiry = sec.bbg.BDP( sec.name, "LAST_TRADEABLE_DT", RT = False )
                days_to_exp = CountBizDays( self.pd, expiry )
                expiry = expiry.strftime( "%d-%b-%Y" )
            except BloombergError:
                expiry = "N/A"
                days_to_exp = 999 # just a large number

            # --- accumulate Potfolio's net and gross exposure
            net_exposure += exposure
            grs_exposure += math.fabs( exposure )
            com_exposure += math.fabs( exposure ) if sec.name.endswith( "COMDTY" ) else 0.0

            positions_table[sec.name] = {
                "exposure": exposure,
                "position": qty / sec.cntSize,
                "weight": weight,
                "pctOfMaxVolume": pct_of_max_vol,
                "beta": beta,
                "bbgBeta": bbg_beta,
                "ownership": ownership,
                "exchange": sec.underlying.undlexch,
                "expiry": expiry,
                # --- color codes for monitored fields
                "weightColor": monitorSingleNameExposure( weight ),
                "pctOfMaxVolumeColor": monitorSingleNameLiquidity( pct_of_max_vol ),
                "ownershipColor": monitorOwnership( ownership, sec.underlying.undlexch ),
                "expiryColor": monitorDaysToExpiration( days_to_exp ),
            }

        aggregates_table = {
            "aum": self.aum,
            "net": net_exposure,
            "gross": grs_exposure,
            "commod": com_exposure,
            "beta": port_beta,
            "index": self.indexes[0].name,
            # --- color codes for monitored fields
            "netColor": monitorNetExposure( net_exposure / self.aum ),
            "grossColor": monitorGrossExposure( grs_exposure / self.aum ),
            "commodColor": monitorCommodExposure( com_exposure / self.aum ),
        }

        self.reports["POS"] = {
            "fund": self.fundname,
            "topic": "POS",
            "report": json.dumps( {
                "timestamp": timestamp,
                "positions": positions_table,
                "aggregates": aggregates_table } ),
        }

        #-----------------------------------------------------------------------
        #   betas by index
        #-----------------------------------------------------------------------
        betas_table = {
            "timestamp": timestamp,
            "header": [ "Index","250 days", "120 days", "60 days", "30 days" ],
            "indexes": [ idx.name for idx in self.indexes ],
        };

        for index in self.indexes:
            betas = []
            for k in [ 250, 120, 60, 30 ]:
                sd = DateRuleApply( self.pd, "-%db" % ( k + 1 ) ).date()
                ed = DateRuleApply( self.pd, "-%db" % 1 ).date()
                _, port_beta, = ComputeBetas( self.fund.positions,
                                              index, self.pd, sd, ed, self.aum )
                betas.append( 100.0 * port_beta )
            betas_table[index.name] = betas

        self.reports["BTS"] = {
            "fund": self.fundname,
            "topic": "BTS",
            "report": json.dumps( betas_table ) }

        logger.info( "done in %s", ( Date.now() - t0 ) )

    ############################################################################
    ##  addRiskMetrics
    ##--------------------------------------------------------------------------
    def addRiskMetrics( self, timestamp ):
        t0 = Date.now()
        logger.info( "adding risk metrics" )

        # --- fetch historical portfolio values
        values = self.fund.PortfolioValues( self.pd, RISKSTDT, self.risk_ed )
        var_values = values.truncate( before = self.risk_sd )

        risks_table = { "timestamp": timestamp }

        for ( tag, n ) in RISK_HORIZONS:
            # --- calculate
            maxloss = ComputeWorstLoss( values, ndays = n )

            # --- calculate 95pct risks at the prescribed horizon
            risks95 = ComputeRiskMetrics( var_values, pctl = 95.0, ndays = n )

            # --- add VaR at 99pct level
            risks99 = ComputeRiskMetrics( var_values, pctl = 99.0, ndays = n )

            risks = {
                "VaR95":  risks95["VaR"],
                "cVaR95": risks95["cVaR"],
                "VaR99":  risks99["VaR"],
                "cVaR99": risks99["cVaR"] }
            risks.update( maxloss )

            risks_table[tag] = {}
            fields_list = []

            for desc, metric, skip in RISK_METRICS:
                if tag in skip:
                    continue

                description = desc % tag
                fields_list.append( description  )

                if tag == "Daily" and tag == "VaR95":
                    risks_table[tag][description] = {
                        "value": risks[metric],
                        "pct": 100*risks[metric] / self.aum,
                        "color": monitorDailyVaR( risks[metric] / self.aum ) }
                elif metric == "MaxLoss":
                    risks_table[tag][description] = {
                        "value": risks[metric],
                        "pct": 100*risks[metric] / self.aum,
                        "more": risks["MaxLossDt"],
                        "color": "plain" }
                else:
                    risks_table[tag][description] = {
                        "value": risks[metric],
                        "pct": 100*risks[metric] / self.aum,
                        "color": "plain" }

            risks_table[tag]["fields"] = fields_list

        var_tree = VaRTree( self.fund, self.pd, self.risk_sd, self.risk_ed, skipCcy = True )
        detailed = { "timestamp": timestamp, "varTree": var_tree }

        self.reports["RSK"] = {
            "fund": self.fundname,
            "topic": "RSK",
            "report": json.dumps( risks_table ) }
        self.reports["DTL"] = {
            "fund": self.fundname,
            "topic": "DTL",
            "report": json.dumps( detailed, sort_keys = True, indent = 4 ) }

        logger.info( "done in %s", ( Date.now() - t0 ) )

    ############################################################################
    ##  addCcyExposures
    ##--------------------------------------------------------------------------
    def addCcyExposures( self, timestamp ):
        t0 = Date.now()
        logger.info( "adding ccy exposures" )

        ccys_exp = ComputeExposures( self.fund.positions, self.pd )
        ccys_table = {}

        self.currencies = []
        for ccy, ( exposure, usd_exposure ) in ccys_exp.iteritems():
            if ccy == "USD" or round( usd_exposure, 0 ) == 0.0:
                continue

            self.currencies.append( "%3sUSD Curncy" % ccy )
            ccys_table[ccy] = {
                "local": exposure,
                "usd": usd_exposure,
                "pct": usd_exposure / self.aum,
            }

        report = {
            "timestamp": timestamp,
            "exposures": ccys_table,
        }

        self.reports["CCY"] = {
            "fund": self.fundname,
            "topic": "CCY",
            "report": json.dumps( report ) }

        logger.info( "done in %s", ( Date.now() - t0 ) )

    ############################################################################
    ##  addStressTests
    ##--------------------------------------------------------------------------
    def addStressTests( self, timestamp ):
        t0 = Date.now()
        logger.info( "adding stress tests" )

        report = StressTestReport( self.pd, STRESS_TEST_SCENARIOS, self.aum, self.fund )
        report.update( { "timestamp": timestamp } )

        self.reports["STRESS"] = {
            "fund": self.fundname,
            "topic": "STRESS",
            "report": json.dumps( report ) }

        logger.info( "done in %s", ( Date.now() - t0 ) )

    ############################################################################
    ##  addCommodSensitivities
    ##--------------------------------------------------------------------------
    def addCommodSensitivities( self, timestamp ):
        t0 = Date.now()
        logger.info( "adding commodity sensitivities" )

        portfolio = ParsePortfolio( self.pd, self.fund, self.aum )

        report = {
            "timestamp": timestamp,
            "exposures": ExposuresAsJson( portfolio, self.commod_sensitivities, SHOCKS ),
        }

        logger.info( "done in %s", ( Date.now() - t0 ) )

        self.reports["CMDTY"] = {
            "fund": self.fundname,
            "topic": "CMDTY",
            "report": json.dumps( report ) }

    ############################################################################
    ##  addPrices
    ##--------------------------------------------------------------------------
    def addPrices( self ):
        t0 = Date.now()
        logger.info( "loading prices" )

        def getInfo( sec ):
            if sec.isccy: return None

            try:
                full_name = sec.bbg.BDP( sec.name, "NAME", RT = False )
                last = sec.lastAdj( self.pd )
                prev = sec.lastAdj( self.pvdt )
            except BloombergError:
                return "error retrieving market info for %s" % sec.name

            try:
                status = sec.bbg.BDP( sec.name, "SIMP_SEC_STATUS", RT = True )
            except BloombergError:
                status = "N/A"

            return { "des": full_name,
                     "sec": sec.name,
                     "stat": status,
                     "pos": self.positions[sec.name],
                     "last": last,
                     "prev": prev,
                     "chg": last / prev - 1.0, }

        securities = sorted( self.fund.positions, key = lambda x: x.name )

        with futures.ThreadPoolExecutor( max_workers = MAXTHREADS ) as exe:
            secInfo = list( exe.map( getInfo, securities ) )

        data = []
        for info in secInfo:
            if info is None:
                continue
            elif isinstance( info, basestring ):
                logger.exception( info )
            else:
                data.append( info )

        self.reports["PRCS"] = {
            "fund": self.fundname,
            "topic": "PRCS",
            "report": json.dumps( data, sort_keys = True ) }

        logger.info( "done in %s", ( Date.now() - t0 ) )

    ############################################################################
    ##  recalc
    ##--------------------------------------------------------------------------
    def recalc( self ):
        posChanged = self.parsePositions()

        # --- if positions have not been loaded yet, skip all other steps
        if self.fund is None:
            return

        timestamp = Date.utcnow().isoformat()

        self.addFundInfo( timestamp )
        self.addPosAndBetas( timestamp )

        if posChanged:
            self.addRiskMetrics( timestamp )

        self.addCcyExposures( timestamp )
        self.addStressTests( timestamp )
        self.addCommodSensitivities( timestamp )
        self.addPrices()

    ############################################################################
    ##  archiveReports
    ##--------------------------------------------------------------------------
    def archiveReports( self ):
        if self.pd == Date.today():
            timestamp = Date.utcnow()
        else:
            timestamp = self.pd.EOD()

        for topic, doc in self.reports.iteritems():
            self.db_coll.update( { "fund": self.fundname, "topic": topic },
                                 { "$set": { "date": timestamp,
                                             "report": doc["report"] } }, upsert = True )

    ############################################################################
    ##  post
    ##--------------------------------------------------------------------------
    def post( self, report ):
        report = urllib.urlencode( report )
        try:
            logger.debug( "posting %d bytes in %s", len( report ), self.url )
            t0 = Date.now()
            urllib2.urlopen( self.url, report, timeout = 60 )
            logger.debug( "posted to %s in %s", self.url, ( Date.now() - t0 ) )
        except ( urllib2.HTTPError, urllib2.URLError ):
            logger.error( "failed to broadcast report to %s", self.url )

    ############################################################################
    ##  broadcast
    ##--------------------------------------------------------------------------
    def broadcast( self ):
        t0 = Date.now()
        logger.info( "posting to %s", self.url )

        with futures.ThreadPoolExecutor( max_workers = MAXTHREADS ) as exe:
            list( exe.map( self.post, self.reports.itervalues() ) )

        logger.info( "done in %s", ( Date.now() - t0 ) )

    ############################################################################
    ##  start
    ##--------------------------------------------------------------------------
    def start( self, stopAt ):
        try:
            version = pkg_resources.require( "Snail" )[0].version
        except pkg_resources.DistributionNotFound:
            version = "DEV"

        logger.info( "Starting Risk Server: Version is %s, "
                     "Pricing Date is %s" % ( version, self.pd ) )

        while Date.now() < stopAt:
            try:
                t0 = Date.now()
                # --- reports are recalculated and archieved every "recalc" seconds
                if t0 > self.t0:
                    self.t0 = t0 + relativedelta( seconds = self.recalc_freq )
                    self.recalc()
                    logger.info( "total report calc time is %s", ( Date.now() - t0 ) )

                    if self.archive:
                        self.archiveReports()

                self.broadcast()

            except Exception:
                logger.critical( "top level exception", exc_info = True )

            time.sleep( self.resend_freq )

################################################################################
##  run
##------------------------------------------------------------------------------
def run( fundname = "main", port = 9000, date = None, archive = True ):
    from Snail.LIB_PortfolioFns import createUnique, Security
    from Snail.LIB_CurveFns import Interpolate

    import os

    mongodb_uri = os.environ.get( "MONGODB_URI", None )
    if not mongodb_uri:
        import user
        mongodb_uri = user.mongodb_uri

    import Snail.CFG_FundParameters as cfg
    cfg.setup_config( cfg.__dict__, fundname )

    pd = date or Date.today()
    nav = Interpolate( cfg.NAVCRV, pd )

    # --- stop server just before midnight
    stopTime = DateRuleApply( Date.today(), "+1b-1d" ).EOD()

    # --- indexes used for beta calculation
    indexes = [
        createUnique( "SX5E Index", "EUR", Security ),
        createUnique( "SXXP Index", "EUR", Security ),
        createUnique( "SX6P Index", "EUR", Security ),
        createUnique( "IBEX Index", "EUR", Security ),
        createUnique( "IBOV Index", "BRL", Security ),
        createUnique(  "SPX Index", "USD", Security ),
    ]
    server = RiskServer( pd = pd, fundname = fundname,
                         url = "%s%d/notify" % ( "http://localhost:", port ),
                         portfolio = cfg.FUNDNAME, aum = nav, indexes = indexes,
                         mongodb_uri = mongodb_uri, archive = archive )
    server.start( stopAt = stopTime )

################################################################################
##  main
##------------------------------------------------------------------------------
def main():
    curr_dt = Date.today()
    strt_dt = Date( curr_dt.year, curr_dt.month, curr_dt.day, 6, 30, 0 )
    # --- sleep until requested start time
    while Date.now() <= strt_dt:
        time.sleep( 300 ) # wait 5 minutes

    argh.dispatch_command( run, namespace = user )

if __name__ == "__main__":
    run( fundname = "main", date = None, archive = False )

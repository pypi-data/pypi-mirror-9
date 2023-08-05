# -*- coding: utf-8 -*-
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
from dateutil.relativedelta import relativedelta

import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.web
import tornado.gen

import futures
import logging
import argh
import user
import os
import zmq
import json
import pymongo

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)-15s %(levelname)-8s %(name)-32s %(message)s"
)
logger = logging.getLogger( __name__ )

################################################################################
## Publisher
##------------------------------------------------------------------------------
class Publisher( tornado.websocket.WebSocketHandler ):
    def initialize( self, fund, topic ):
        self.fund = fund
        self.topic = topic

    def open( self ):
        self.application.subscribers[self.fund][self.topic].add( self )
        # --- load latest report from mongodb
        cutoff = Date.utcnow() - relativedelta( minutes = 15 )
        db_conn = pymongo.MongoClient( self.application.mongodb_uri ).get_default_database()
        db_coll = db_conn["snail"]["RiskServer"]
        records = db_coll.find( { "fund": self.fund,
                                  "topic": self.topic,
                                  "date": { "$gte": cutoff } } ).sort( "date", pymongo.DESCENDING )
        if records.count():
            self.write_message( records[0]["report"] )

    def on_close( self ):
        self.application.subscribers[self.fund][self.topic].remove( self )

################################################################################
## IndexHandler
##------------------------------------------------------------------------------
class IndexHandler( tornado.web.RequestHandler ):
    def get( self ):
        self.render( "index.html", funds = self.application.funds )

################################################################################
## DetailedHandler
##------------------------------------------------------------------------------
class DetailedHandler( tornado.web.RequestHandler ):
    def initialize( self, fund ):
        self.fund = fund

    def get( self ):
        self.render( "detailed.html", fund = self.fund )

################################################################################
## NotifyHandler
##------------------------------------------------------------------------------
class NotifyHandler( tornado.web.RequestHandler ):
    def post( self ):
        fund = self.get_argument( "fund" )
        topic = self.get_argument( "topic" )
        report = self.get_argument( "report" )
        self.application.broadcast( fund, topic, report )

################################################################################
## ReportsHandler
##------------------------------------------------------------------------------
class ReportsHandler( tornado.web.RequestHandler ):
    def initialize( self, url ):
        self.url = url

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post( self ):
        message = {
            "report": str( self.get_argument( "report" ) ),
            "parms": json.loads( str( self.get_argument( "parms" ) ) ),
        }
        app = self.application
        data = yield tornado.gen.Task( app.async, app.ondemand,
                                       self.url, message, self.request.remote_ip )
        self.write( data )

################################################################################
##  SnailWebServer
##------------------------------------------------------------------------------
class SnailWebServer( tornado.web.Application ):
    ############################################################################
    ##  Initialization
    ##--------------------------------------------------------------------------
    def __init__( self, topics, funds, mongodb_uri, handlers = None, **kwds ):
        self.funds = funds

        # --- create handlers for websockets
        websockets = []
        for fund in self.funds:
            websockets += [ ( r"^/%s/%s$" % ( fund, topic ),
                            Publisher, { "fund": fund, "topic": topic } ) for topic in topics ]

        # --- websocket handlers need to be registered before the page handlers,
        #     so they don’t get masked.
        handlers = websockets + ( handlers or [] )

        super( SnailWebServer, self ).__init__( handlers = handlers, **kwds )
        self.subscribers = { fund: { topic: set() for topic in topics } for fund in self.funds }

        self.executor = futures.ThreadPoolExecutor( max_workers = 10 )
        self.context = zmq.Context()

        self.mongodb_uri = mongodb_uri

    ############################################################################
    ##  broadcast
    ##--------------------------------------------------------------------------
    def broadcast( self, fund, topic, msg ):
        for conn in self.subscribers[fund][topic]:
            try:
                conn.write_message( msg )
            except:
                logger.critical( "error sending report to %s" % topic, exc_info = True )

    ############################################################################
    ##  ondemand
    ##--------------------------------------------------------------------------
    def ondemand( self, url,  message, remote_ip ):
        socket = self.context.socket( zmq.REQ )
        socket.connect( url )
        socket.send_pyobj( ( remote_ip, message ) )
        data = socket.recv_string()
        socket.close()
        return data

    ############################################################################
    ##  wrap_callback
    ##--------------------------------------------------------------------------
    def wrap_callback( self, callback ):
        def wrapped( f ):
            err = f.exception()
            if err is None:
                return callback( f.result() )
            else:
                return callback( err )
        return wrapped

    ############################################################################
    ##  async
    ##--------------------------------------------------------------------------
    def async( self, func, *args, **kwds ):
        callback = kwds.pop( "callback", None )
        future = self.executor.submit( func, *args, **kwds )
        if callback is not None:
            future.add_done_callback( self.wrap_callback( callback ) )
        return future

    ############################################################################
    ##  __del__
    ##--------------------------------------------------------------------------
    def __del__( self ):
        self.executor.shutdown()

################################################################################
##  run
##------------------------------------------------------------------------------
def run( port = 9000, ondemandport = 5000 ):
    mongodb_uri = os.environ.get( "MONGODB_URI", None )
    if not mongodb_uri:
        import user
        mongodb_uri = user.mongodb_uri

    root = os.path.join( os.path.dirname( __file__ ), "www" )
    srvurl = "%s:%d" % ( "tcp://127.0.0.1", ondemandport )

    app = SnailWebServer(
        topics = [ "INFO", "POS", "RSK", "CCY", "BTS", "DTL", "STRESS", "CMDTY", "PRCS" ],
        funds = [ "main", "mcp" ],
        mongodb_uri = mongodb_uri,
        handlers = [
            ( r"^/main/?$", DetailedHandler, { "fund": "main" } ),
            ( r"^/mcp/?$", DetailedHandler, { "fund": "mcp" } ),
            ( r"^/notify$", NotifyHandler ),
            ( r"^/ondemand$", ReportsHandler, { "url": srvurl } ),
            ( r"/.*", IndexHandler ),
        ],
        template_path = os.path.join( root, "templates" ),
        static_path = os.path.join( root, "static" ),
    )

    http_server = tornado.httpserver.HTTPServer( app )
    http_server.listen( port, address = "127.0.0.1" )
    tornado.ioloop.IOLoop.instance().start()

################################################################################
##  main
##------------------------------------------------------------------------------
def main():
    argh.dispatch_command( run, namespace = user )

################################################################################
##  for interactive use
##------------------------------------------------------------------------------
if __name__ == "__main__":
    os.environ["MONGODB_URI"] = "mongodb://localhost/csbraccia"
    run()
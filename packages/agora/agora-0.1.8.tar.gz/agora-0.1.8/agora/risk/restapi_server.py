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

from onyx.core import (GetObj, ObjNamesByType, ObjNotFound,
                       GetVal, InvalidateNode)
from agora.corelibs.onyx_utils import OnyxInit

import onyx.database as onyx_db

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.escape

import psycopg2
import argh
import functools
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-15s %(levelname)-8s %(name)-32s %(message)s"
)
logger = logging.getLogger(__name__)


###############################################################################
class ObjectsHandler(tornado.web.RequestHandler):
    # -------------------------------------------------------------------------
    def get(self, obj_type=None):
        response = ObjNamesByType(obj_type)

        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.write(json.dumps(response))


###############################################################################
class FundHandler(tornado.web.RequestHandler):
    # -------------------------------------------------------------------------
    def get(self, fund_name):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")

        try:
            obj = GetObj(tornado.escape.url_unescape(fund_name))
        except ObjNotFound as err:
            self.set_status(404)
            self.write(json.dumps(str(err)))
        else:
            portfolio = GetVal(obj.Name, "Portfolio")
            children = sorted(GetVal(portfolio, "Children").keys())

            response = {
                "aum": GetVal(obj.Name, "Nav"),
                "portfolios": children,
            }

            self.set_status(200)
            self.write(json.dumps(response))


###############################################################################
class PositionsHandler(tornado.web.RequestHandler):
    # -------------------------------------------------------------------------
    def get(self, book):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")

        try:
            response = GetVal(tornado.escape.url_unescape(book), "Deltas")
        except ObjNotFound as err:
            response = str(err)
            self.set_status(404)
        else:
            self.set_status(200)

        self.write(json.dumps(response))


###############################################################################
class FxHandler(tornado.web.RequestHandler):
    # -------------------------------------------------------------------------
    def get(self, book):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")

        try:
            response = GetVal(tornado.escape.url_unescape(book), "FxExposures")
        except ObjNotFound as err:
            response = str(err)
            self.set_status(404)
        else:
            self.set_status(200)

        self.write(json.dumps(response))


###############################################################################
class RiskRESTServer(tornado.web.Application):
    # -------------------------------------------------------------------------
    def __init__(self, handlers=None, **kwds):
        super().__init__(handlers, **kwds)

        self.conn = onyx_db.obj_clt.conn
        io_loop = tornado.ioloop.IOLoop.instance()

        # --- listen on one or more channels
        self.listen("poseffects")

        # --- handler
        handler = functools.partial(self.receive, callback=self.poseffects)

        # --- add event receiver to tornado's IOLoop
        io_loop.add_handler(self.conn.fileno(), handler, io_loop.READ)

    # -------------------------------------------------------------------------
    def listen(self, channel):
        curs = self.conn.cursor()
        curs.execute("LISTEN {0:s};".format(channel))

    # -------------------------------------------------------------------------
    def receive(self, fd, events, callback):
        state = self.conn.poll()
        if state == psycopg2.extensions.POLL_OK:
            if self.conn.notifies:
                callback(self.conn.notifies.pop())

    # -------------------------------------------------------------------------
    def poseffects(self, msg):
        if msg.channel == "poseffects":
            # --- on this channel, payload is the bookname with changed
            #     positions
            InvalidateNode(msg.payload, "Children")
            logger.info("Children of '{0:s}' invalidated".format(msg.payload))


# -----------------------------------------------------------------------------
def run(dbname="ProdDb", port=6666):
    with OnyxInit(dbname):
        app = RiskRESTServer(handlers=[
            (r"/objects$", ObjectsHandler),
            (r"/objects/(\w+$)", ObjectsHandler),
            (r"/funds/(.+)", FundHandler),
            (r"/positions/(.+)", PositionsHandler),
            (r"/fxexposures/(.+)", FxHandler),
        ])

        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port, address="127.0.0.1")
        tornado.ioloop.IOLoop.instance().start()


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    run()

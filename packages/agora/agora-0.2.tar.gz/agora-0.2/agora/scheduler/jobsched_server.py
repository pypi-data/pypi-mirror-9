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

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import agora.scheduler.jobsched_fns

import tornado.httpserver
import tornado.ioloop
import tornado.web

import argh
import logging
import os

SQLITE_PATH = os.path.join(os.getenv("HOME"), ".jobs.sqlite")
LOG_FMT = "%(asctime)-15s %(levelname)-8s %(name)-38s %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FMT)
jobs_logger = logging.getLogger(__name__)

jobs_stores = {
    "default": SQLAlchemyJobStore(url="sqlite:///{0:s}".format(SQLITE_PATH)),
}

jobs_executors = {
    "default": ThreadPoolExecutor(20),
    "processpool": ProcessPoolExecutor(2)
}


# -----------------------------------------------------------------------------
def run(port=9100):
    app = agora.scheduler.jobsched_fns.SchedulingServer(
        jobs_logger,
        jobs_stores,
        jobs_executors,
        handlers=[
            (r"/jobs$", agora.scheduler.jobsched_fns.JobsHandler),
            (r"/jobs/(\w+$)", agora.scheduler.jobsched_fns.JobsHandler),
        ],
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    run()

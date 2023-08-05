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
"""
Scheduling functions and request handlers.
"""
from onyx.core import Date

from apscheduler.schedulers.tornado import TornadoScheduler

import tornado.web
import importlib
import json
import os


##-----------------------------------------------------------------------------
def run_job(mod_name, package_name, args, kwds):
    module = importlib.import_module(mod_name, package_name)
    module.main(Date.today(), *args, **kwds)


###############################################################################
class IndexHandler(tornado.web.RequestHandler):
    ##-------------------------------------------------------------------------
    def initialize(self, index_file):
        self.index_file = index_file

    ##-------------------------------------------------------------------------
    def get(self):
        with open(self.index_file, "r") as index_file:
            self.write(index_file.read())
#        self.render(self.index_file)


###############################################################################
class PendingJobsHandler(tornado.web.RequestHandler):
    ##-------------------------------------------------------------------------
    def get(self):
        jobs = []
        for job in self.application.scheduler.get_jobs():
            jobs.append({
                "name": job.name,
                "id": job.id,
                "executor": job.executor,
                "next_run_time": job.next_run_time.isoformat(),
                "trigger": {field.name: str(field)
                            for field in job.trigger.fields},
            })

        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.write(json.dumps(jobs))


###############################################################################
class ModifyJobHandler(tornado.web.RequestHandler):
    ##-------------------------------------------------------------------------
    def post(self):
        job_parms = json.loads(self.request.body.decode("utf-8"))

        if job_parms["id"] is None:
            self.application.schedule_job({
                "module": job_parms["name"],
                "trigger": job_parms["trigger"]
            })

        else:
            job_id = str(job_parms["id"])
            changes = {"executor": job_parms["executor"]}
            changes.update(job_parms["trigger"])
            self.application.scheduler.modify_job(job_id, changes)


###############################################################################
class SchedulingServer(tornado.web.Application):
    ##-------------------------------------------------------------------------
    def __init__(self, logger, handlers=None, **kwds):
        super().__init__(handlers, **kwds)

        self.scheduler = TornadoScheduler(logger=logger)
        self.scheduler.start()

    ##-------------------------------------------------------------------------
    def schedule_job(self, job):
        parts = job["module"].split(".")
        mod_name = "{0:s}{1:s}".format("."*(len(parts)-1), parts[-1])
        pak_name = ".".join(parts[:-1])

        kwargs = {
            "mod_name": mod_name,
            "package_name": pak_name,
            "args": job.get("args", []),
            "kwds": job.get("kwds", {}),
        }

        # --- each job is scheduled using a wrapper
        self.scheduler.add_job(run_job, kwargs=kwargs,
                               trigger="cron",
                               name=job["module"],
                               replace_existing=True, **job["trigger"])

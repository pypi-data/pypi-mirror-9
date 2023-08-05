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
Scheduling functions and request handlers implementing a RESTful API.
"""
from onyx.core import Date

from apscheduler.schedulers.tornado import TornadoScheduler

import apscheduler.jobstores.base
import tornado.web
import importlib
import json

__all__ = [
    "SchedulerError",
    "IndexHandler",
    "JobsHandler",
    "SchedulingServer"
]


##-----------------------------------------------------------------------------
def run_job(mod_name, args, kwds):
    module = importlib.import_module(mod_name)
    module.main(Date.today(), *args, **kwds)


###############################################################################
class SchedulerError(Exception):
    pass


###############################################################################
class IndexHandler(tornado.web.RequestHandler):
    ##-------------------------------------------------------------------------
    def initialize(self, index_file):
        self.index_file = index_file

    ##-------------------------------------------------------------------------
    def get(self):
        with open(self.index_file, "r") as index_file:
            self.write(index_file.read())


###############################################################################
class JobsHandler(tornado.web.RequestHandler):
    ##-------------------------------------------------------------------------
    def get(self, job_id=None):
        self.application.logger.info("GET: job_id is {0!s}".format(job_id))

        if job_id is None:
            # --- return all pending jobs
            response = []
            for job in self.application.scheduler.get_jobs():
                if job.next_run_time is None:
                    next_run_time = "paused"
                else:
                    next_run_time = job.next_run_time.isoformat()

                response.append({
                    "name": job.name,
                    "id": job.id,
                    "executor": job.executor,
                    "next_run_time": next_run_time,
                    "trigger": {field.name: str(field)
                                for field in job.trigger.fields},
                })

        else:
            response = "Not implemented...\n"

        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.write(json.dumps(response))

    ##-------------------------------------------------------------------------
    def put(self, job_id=None):
        self.application.logger.info("PUT: job_id is {0!s}".format(job_id))

        if job_id is None:
            self.set_status(404)
            return

        changes = json.loads(self.request.body.decode("utf-8"))
        trigger_args = changes.pop("trigger", None)
        job_status = changes.pop("next_run_time", None)

        try:
            self.application.scheduler.modify_job(job_id, **changes)
            if trigger_args is not None:
                self.application.scheduler.reschedule_job(job_id,
                                                          trigger="cron",
                                                          **trigger_args)
                self.application.logger.info("PUT: job was rescheduled")

            if job_status == "pause":
                self.application.paused.add(job_id)
                self.application.scheduler.pause_job(job_id)
                self.application.logger.info("PUT: job was paused")

            elif job_status == "resume":
                if job_id in self.application.paused:
                    self.application.scheduler.resume_job(job_id)
                    self.application.paused.remove(job_id)
                    self.application.logger.info("PUT: job was resumed")

        except apscheduler.jobstores.base.JobLookupError as err:
            self.set_status(404)
            self.write("{0!s}\n".format(err))

    ##-------------------------------------------------------------------------
    def delete(self, job_id=None):
        self.application.logger.info("DELETE: job_id is {0!s}".format(job_id))

        if job_id is None:
            self.set_status(404)
            return

        try:
            self.application.scheduler.remove_job(job_id)
        except apscheduler.jobstores.base.JobLookupError as err:
            self.set_status(404)
            self.write("{0!s}\n".format(err))

    ##-------------------------------------------------------------------------
    def post(self, job_id=None):
        self.application.logger.info("POST: job_id is {0!s}".format(job_id))

        if job_id is not None:
            self.set_status(404)
            return

        job_parms = json.loads(self.request.body.decode("utf-8"))
        try:
            self.application.schedule_job({
                "module": job_parms["name"],
                "trigger": job_parms["trigger"]
            })
            self.set_status(201)
        except SchedulerError as err:
            self.set_status(400)
            self.write("{0!s}\n".format(err))


###############################################################################
class SchedulingServer(tornado.web.Application):
    ##-------------------------------------------------------------------------
    def __init__(self, logger, jobstores, executors, handlers=None, **kwds):
        super().__init__(handlers, **kwds)

        self.logger = logger
        self.scheduler = TornadoScheduler(logger=logger,
                                          jobstores=jobstores,
                                          executors=executors)
        self.scheduler.start()

        self.paused = set()
        for job in self.scheduler.get_jobs():
            if job.next_run_time is None:
                self.paused.add(job.id)

    ##-------------------------------------------------------------------------
    def schedule_job(self, job):
        mod_name = job["module"]

        # --- is the module importable and does it expose a main function?
        try:
            module = importlib.import_module(mod_name)
        except (ImportError, SystemError) as err:
            raise SchedulerError("{0!s}".format(err))

        if not hasattr(module, "main"):
            raise SchedulerError("{0:s} doesn't expose a main "
                                 "function".format(job["module"]))

        kwargs = {
            "mod_name": mod_name,
            "args": job.get("args", []),
            "kwds": job.get("kwds", {}),
        }

        # --- each job is scheduled using a wrapper
        return self.scheduler.add_job(run_job, kwargs=kwargs,
                                      trigger="cron",
                                      name=job["module"],
                                      replace_existing=True, **job["trigger"])

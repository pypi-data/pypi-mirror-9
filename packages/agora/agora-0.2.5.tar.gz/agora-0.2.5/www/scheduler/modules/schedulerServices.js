/*#############################################################################
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
#############################################################################*/

angular.module("schedulerServices", [])
    .factory("jobs", ["$http", function($http){
        return {
            getScheduled: function(onSuccess){
                $http.get("http://localhost:9100/jobs")
                    .success(function(response){
                        // first do some pre-processing
                        response.forEach(function(row){
                            if (row.next_run_time == "paused"){
                                row.running = false;
                            } else {
                                row.next_run_time = new Date(row.next_run_time);
                                row.running = true;
                            };
                        });
                        // then call the onSuccess callback
                        onSuccess(response);
                    })
                    .error(function(data, status, headers, config){
                        console.log(data);
                    });
            },

            uploadNew: function(job, onSuccess){
                $http.post("http://localhost:9100/jobs",
                           job,
                           {headers: {"Content-Type":
                                      "application/x-www-form-urlencoded"}})
                    .success(function(response){
                        onSuccess(response);
                    })
                    .error(function(data, status, headers, config){
                        console.log(data);
                    });
            },

            uploadModified: function(job, onSuccess){
                job_id = job["id"];
                changes = {
                    "executor": job["executor"],
                    "trigger": job["trigger"],
                };
                $http.put("http://localhost:9100/jobs/" + job_id,
                          changes,
                          {headers: {"Content-Type":
                                     "application/x-www-form-urlencoded"}})
                    .success(function(response){
                        onSuccess(response);
                    })
                    .error(function(data, status, headers, config){
                        console.log(data);
                    });
            },

            deleteJob: function(job_id, onSuccess){
                $http.delete("http://localhost:9100/jobs/" + job_id)
                    .success(function(response){
                        onSuccess(response);
                    })
                    .error(function(data, status, headers, config){
                        console.log(data);
                    });
            },
    
            pauseJob: function(job_id, onSuccess){
                changes = {"next_run_time": "pause"};
                $http.put("http://localhost:9100/jobs/" + job_id,
                          changes,
                          {headers: {"Content-Type":
                                     "application/x-www-form-urlencoded"}})
                    .success(function(response){
                        onSuccess(response);
                    })
                    .error(function(data, status, headers, config){
                        console.log(data);
                    });
            },
    
            resumeJob: function(job_id, onSuccess){
                changes = {"next_run_time": "resume"};
                $http.put("http://localhost:9100/jobs/" + job_id,
                          changes,
                          {headers: {"Content-Type":
                                     "application/x-www-form-urlencoded"}})
                    .success(function(response){
                        onSuccess(response);
                    })
                    .error(function(data, status, headers, config){
                        console.log(data);
                    });
            },
        };
    }]);
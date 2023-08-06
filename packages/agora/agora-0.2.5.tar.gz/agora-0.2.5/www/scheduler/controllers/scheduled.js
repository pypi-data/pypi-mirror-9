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

angular.module("jobsSchedulerApp")
    .controller("JobsCtrl", function($scope, $modal, jobs){

        // add watcher
        $scope.$watch($scope.jobs,
                      function(newValue, oldValue){
            if (newValue !== oldValue){
                jobs.scheduled = $scope.jobs;
            };
        });

        $scope.refresh = function(){
            jobs.getScheduled(function(response){
                $scope.jobs = response;
            })
        };

        $scope.openModal = function(job, isNew){
            var instance = $modal.open({
                templateUrl: "templates/edit.tpl.html",
                controller: "EditCtrl",
                resolve: {
                    job: function(){ return job; },
                }
            });
            instance.result.then(function(job){
                if (isNew){
                    console.log("uploading new job");
                    jobs.uploadNew(job, function(response){
                        $scope.refresh();
                    });
                } else {
                    console.log("modifying existing job");
                    jobs.uploadModified(job, function(response){
                        $scope.refresh();
                    });
                };
            }, function(){
                console.log("Modal dismissed at: " + new Date());
            });
        };

        $scope.modifyJob = function(idx, action){
            switch (action){
                case "edit":
                    $scope.openModal(angular.copy($scope.jobs[idx]), false);
                    break;
                case "remove":
                    console.log("deleting " + $scope.jobs[idx]["id"]);
                    jobs.deleteJob($scope.jobs[idx]["id"], function(response){
                        $scope.refresh();
                    });
                    break;
                case "pause":
                    console.log("pausing " + $scope.jobs[idx]["id"]);
                    jobs.pauseJob($scope.jobs[idx]["id"], function(response){
                        $scope.refresh();
                    });
                    break;
                case "resume":
                    console.log("restarting " + $scope.jobs[idx]["id"]);
                    jobs.resumeJob($scope.jobs[idx]["id"], function(response){
                        $scope.refresh();
                    });
                    break;
            };
        };

        $scope.newJob = function(){
            var job = {
                id: null,
                name: "",
                executor: "default",
                trigger: {
                    year: "*",
                    month: "*",
                    week: "*",
                    day: "*",
                    hour: "*",
                    minute: "*",
                    second: "0",
                    day_of_week: "*",
                },
            };
            $scope.openModal(job, true);
        };

        // load jobs
        $scope.refresh();
    });
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

angular.module("riskServerApp")
    .controller("AttributionsCtrl", function($scope, fund, report){
        $scope.attributions = fund.getRiskAttributions(report.parms.port);

        // add watcher
        $scope.$watch(function(){return report.parms.port;},
                      function(newValue, oldValue){
            if (newValue !== oldValue){
                $scope.attributions = fund.getRiskAttributions(newValue);
            };
        });

        var chartOptions = {
            width: 450,
            height: 250,
            chartArea: {left: 10, top: 10, width: "95%", height: "95%"},
        };

        for (var key in $scope.attributions){
            if ($scope.attributions.hasOwnProperty(key)){
                $scope[key] = {
                    data: new google.visualization.DataTable($scope.attributions[key]),
                    options: chartOptions,
                };
            };
        };
    });
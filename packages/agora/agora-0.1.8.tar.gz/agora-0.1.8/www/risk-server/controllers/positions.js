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
    .controller("PositionsCtrl", function($scope, fund, report, baseValidator){
        $scope.fund = fund.getFundInfo(report.parms.fund);
        $scope.positions = fund.getPositions(report.parms.port);

        // add watchers
        $scope.$watch(function(){return report.parms.fund;},
                      function(newValue, oldValue){
            if (newValue !== oldValue){
                $scope.fund = fund.getFundInfo(newValue);
            };
        });

        $scope.$watch(function(){return report.parms.port;},
                      function(newValue, oldValue){
            if (newValue !== oldValue){
                $scope.positions = fund.getPositions(newValue);
            };
        });

        $scope.colorByPos = function(pos){
            if (pos < 0.0){
                return "red";
            } else {
                return "green";
            };
        };

        // add validators
        $scope.validateWeight = function(weight){
            return baseValidator(Math.abs(weight), 0.15);
        };

        $scope.validateDays = function(days){
            return baseValidator(days, 5.0);
        };
    });
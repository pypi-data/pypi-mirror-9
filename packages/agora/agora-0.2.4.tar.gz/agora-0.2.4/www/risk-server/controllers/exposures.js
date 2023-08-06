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
    .controller("ExposuresCtrl", function($scope, fund, report, baseValidator){
        $scope.parms = report.parms;
        $scope.fund = fund.getFundInfo(report.parms.fund);
        $scope.exposures = fund.getRiskExposures(report.parms.port);

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
                $scope.exposures = fund.getRiskExposures(newValue);
            };
        });

        // add validators
        $scope.validateGross = function(){
            return baseValidator($scope.exposures.gross/$scope.fund.aum, 3.0);
        };

        $scope.validateNet = function(){
            return baseValidator(Math.abs($scope.exposures.net/$scope.fund.aum), 0.50);
        };

        $scope.validateCommod = function(){
            return baseValidator(Math.abs($scope.exposures.commod/$scope.fund.aum), 0.333);
        };
    });
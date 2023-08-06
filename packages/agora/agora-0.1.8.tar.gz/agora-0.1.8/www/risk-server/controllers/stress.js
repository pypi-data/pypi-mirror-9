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
    .controller("StressCtrl", function($scope, fund, report){
        $scope.fund = fund.getFundInfo(report.parms.fund);
        $scope.stressScenarios = fund.getStressScenarios(report.parms.fund);

        var length = 2*$scope.stressScenarios.scenarios.length;
        $scope.range = Array.apply(null, Array(length)).map(function(x, i){ return i; })

        $scope.change = function(pos, i){
            k = Math.floor(i / 2);
            return 100.0 * pos[$scope.stressScenarios.scenarios[k]];
        };

        $scope.pnl = function(pos, i){
            k = Math.floor(i / 2);
            chg = pos[$scope.stressScenarios.scenarios[k]];
            return 100.0 * pos.exposure / $scope.fund.aum * chg;
        };
    
        $scope.totalPnL = function(scenario){
            var total = 0.0;
            $scope.stressScenarios.positions.forEach(function(pos){
                total += pos.exposure / $scope.fund.aum * pos[scenario];
            });
            return 100.0*total;
        };

    });
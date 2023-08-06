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

angular.module("agoraGoogleCharts", [])
    .directive("googlePieChart", ["$interval", function($interval){
        return {
            restrict: "A",
            scope: {
                parms: "=parms",
            },
            link: function(scope, element, attrs){
                var chart = new google.visualization.PieChart(element[0]);
                var drawn = false;

                function redraw(){
                    if (element.css("visibility") == "hidden"){
                        drawn = false;
                    } else {
                        if (!drawn){
                            chart.draw(scope.parms.data, scope.parms.options);
                            drawn = true;
                        };
                    };
                };

                redrawId = $interval(redraw, 2000)

                element.on("destroy", function(){
                    $interval.cancel(redrawId);
                });

                // add watcher
                scope.$watch(function(){return scope.parms.data;},
                             function(newValue, oldValue){
                    if (newValue !== oldValue){
                        chart.draw(newValue, scope.parms.options);
                        drawn = true;
                    };
                });
            },
        };
    }]);
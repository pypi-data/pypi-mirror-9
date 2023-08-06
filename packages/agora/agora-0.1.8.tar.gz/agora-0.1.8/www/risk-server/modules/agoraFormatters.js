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

angular.module("agoraFormatters", [])
    .directive("capitalize", function(){
        return {
            require: "ngModel",
            link: function(scope, element, attrs, modelCtrl){
                var capitalize = function(inputValue){
                    if (inputValue == undefined){
                        inputValue = "";
                    };
                    var capitalized = inputValue.toUpperCase();
                    if (capitalized !== inputValue){
                        modelCtrl.$setViewValue(capitalized);
                        modelCtrl.$render();
                    };
                    return capitalized;
                };
                modelCtrl.$parsers.push(capitalize);
                // capitalize initial value
                capitalize(scope[attrs.ngModel]);
            }
        };
    })
    .directive("numberFormat", ["$filter", "$parse", function($filter, $parse){
        return {
            require: "ngModel",
            link: function(scope, element, attrs, modelCtrl){

                var decimals = $parse(attrs.decimals)(scope);
    
                modelCtrl.$parsers.push(function(data){
                    // Attempt to convert user input into a numeric type to store
                    // as the model value (otherwise it will be stored as a string)
                    // NOTE: Return undefined to indicate that a parse error has occurred
                    //       (i.e. bad user input)
                    var parsed = parseFloat(data);
                    return !isNaN(parsed) ? parsed : undefined;
                });
          
                modelCtrl.$formatters.push(function(data){
                    // convert data from model format to view format
                    return $filter("number")(data, decimals); //converted
                });
    
                element.bind("focus", function(){
                    element.val(modelCtrl.$modelValue);
                });
    
                element.bind("blur", function(){
                    // Apply formatting on the stored model value for display
                    var formatted = $filter("number")(modelCtrl.$modelValue, decimals);
                    element.val(formatted);
                });
            }
        };
    }]);
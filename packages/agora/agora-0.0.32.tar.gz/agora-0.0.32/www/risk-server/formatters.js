angular.module("formatters", [])
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
                    //convert data from model format to view format
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
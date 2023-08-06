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

angular.module("agoraServices", [])
    .factory("fund", ["$http", function($http){
        return {
            // to be reimplemented with queries to the REST API server
            getFunds: function(){
                return ["ABC Turbo Long/Short", "ABC Turbo Sustainable"];
            },
            getFundInfo: function(name){
                return {
                    aum: 70000000,
                    ccy: "USD",
                    portfolios: ["Master", "Fundamental", "Event", "Opportunistic", "Relative Value"],
                };
            },
            getPositions: function(port){
                if (port=="Master"){
                    return MASTER_POSITIONS;
                } else if (port == "Fundamental"){
                    return FUNDAMENTAL_POSITIONS;
                } else {
                    return [];
                };
            },
            getRiskExposures: function(port){
                var aum = 70000000;

                if (port=="Master"){
                    return {
                        gross: 1.35*aum,
                        net: -0.05*aum,
                        commod: 0.04*aum,
                        metrics: [
                            {description: "Daily VaR (95%)", value: 0.013*aum},
                            {description: "Daily VaR (99%)", value: 0.018*aum},
                            {description: "Weekly VaR (95%)", value: 0.016*aum},
                            {description: "Monthly VaR (95%)", value: 0.021*aum},
                            {description: "Worst Day", value: 0.026*aum, extra: "21-Aug-2011"},
                            {description: "Worst Week", value: 0.038*aum, extra: "18-Aug-2011"},
                            {description: "Worst Month", value: 0.056*aum, extra: "17-Aug-2011"}],
                        betas: [
                            {index: "SX5E INDEX", values: [0.18, 0.15, 0.17, 0.11]},
                            {index: "SX6P INDEX", values: [0.18, 0.15, 0.17, 0.11]}],
                    };
                } else {
                    return {
                        gross: 0.35*aum,
                        net: 0.15*aum,
                        commod: 0.0*aum,
                        risks: [],
                        betas: [],
                    };            
                };
            },
            getRiskAttributions: function(port){
                return {
                    grossByRegion: GROSS_BY_REGION,
                    grossBySector: GROSS_BY_SECTOR,
                    varByRegion: VAR_BY_REGION,
                    varBySector: VAR_BY_SECTOR,
                };
            },
            getStressScenarios: function(port){
                return STRESS_SCENARIOS;
            },
        };
    }])
    .factory("report", function(){
        var parms = {
            date: new Date(),
            fund: "",
            port: "",
        };

        return {
            setDate: function(date){ parms.date = date; },
            setFund: function(fund){ parms.fund = fund; },
            setPort: function(port){ parms.port = port; },
            parms: parms,
        };
    });

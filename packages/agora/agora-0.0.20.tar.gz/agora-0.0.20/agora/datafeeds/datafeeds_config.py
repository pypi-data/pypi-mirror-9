###############################################################################
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
###############################################################################

from onyx.core import Table

BBG_MAPPING = Table([
    ["Bloomberg", "WSJ", "Google", "Yahoo"],
    # --- Italy
    ["A2A:IM", "A2A:IT", "BIT:A2A", "A2A.MI"],
    ["ASC:IM", "ASC:IT", "BIT:ASC", "ASC.MI"],
    ["ACE:IM", "ACE:IT", "BIT:ACE", "ACE.MI"],
    ["ENEL:IM", "ENEL:IT", "BIT:ENEL", "ENEL.MI"],
    ["EGPW:IM", "EGPW:IT", "BIT:EGPW", "EGPW.MI"],
    ["SAL:IM", "SAL:IT", "BIT:SAL", "SAL.MI"],
    ["AST:IM", "AST:IT", "BIT:AST", "AST.MI"],
    ["ERG:IM", "ERG:IT", "BIT:ERG", "ERG.MI"],
    ["ATl:IM", "ATL:IT", "BIT:ATL", "ATL.MI"],
    ["FKR:IM", "FKR:IT", "BIT:FKR", "FKR.MI"],
    ["HER:IM", "HER:IT", "BIT:HER", "HER.MI"],
    ["IRE:IM", "IRE:IT", "BIT:IRE", "IRE.MI"],
    ["SRG:IM", "SRG:IT", "BIT:SRG", "SRG.MI"],
    ["TRN:IM", "TRN:IT", "BIT:TRN", "TRN.MI"],
    ["PRY:IM", "PRY:IT", "BIT:PRY", "PRY.MI"],
    # --- Portugal
    ["EDP:PL", "EDP:PT", "ELI:EDP", "EDP.LS"],
    ["EDPR:PL", "EDPR:PT", "ELI:EDPR", "EDPR.LS"],
    ["RENE:PL", "RENE:PT", "ELI:RENE", "RENE.LS"],
    # --- Spain
    ["ABE:SM", "ABE:ES", "BME:ABE", "ABE.MC"],
    ["ABG:SM", "ABG:ES", "BME:ABG", "ABG.MC"],
    ["ABG/P:SM", "ABGP:ES", "BME:ABG.P", "ABG-P.MC"],
    ["ACS:SM", "ACS:ES", "BME:ACS", "ACS.MC"],
    ["ANA:SM", "ANA:ES", "BME:ANA", "ANA.MC"],
    ["ELE:SM", "ELE:ES", "BME:ELE", "ELE.MC"],
    ["ENC:SM", "ENC:ES", "BME:ENC", "ENC.MC"],
    ["FCC:SM", "FCC:ES", "BME:FCC", "FCC.MC"],
    ["FER:SM", "FER:ES", "BME:FER", "FER.MC"],
    ["GAM:SM", "GAM:ES", "BME:GAM", "GAM.MC"],
    ["GAS:SM", "GAS:ES", "BME:GAS", "GAS.MC"],
    ["IBE:SM", "IBE:ES", "BME:IBE", "IBE.MC"],
    ["OHL:SM", "OHL:ES", "BME:OHL", "OHL.MC"],
    # --- UK
    ["SSE:LN", "SSE:UK", "LON:SSE", "SSE.L"],
    ["CNA:LN", "CNA:UK", "LON:CNA", "CNA.L"],
    ["DRX:LN", "DRX:UK", "LON:DRX", "DRX.L"],
    ["PNN:LN", "PNN:UK", "LON:PNN", "PNN.L"],
    ["UU/:LN", "UU.:UK", "LON:UU", "UU.L"],
    ["SVT:LN", "SVT:UK", "LON:SVT", "SVT.L"],
    ["NG/:LN", "NG.:UK", "LON:NG", "NG.L"],
    ["INFI:LN", "INFI:UK", "LON:INFI", "INFI.L"],
    # --- France
    ["FGR:FP", "FGR:FR", "EPA:FGR", "FGR.PA"],
    ["DG:FP", "DG:FR", "EPA:DG", "DG.PA"],
    ["VIE:FP", "VIE:FR", "EPA:VIE", "VIE.PA"],
    ["SEV:FP", "SEV:FR", "EPA:SEV", "SEV.PA"],
    ["GSZ:FP", "GSZ:FR", "EPA:GSZ", "GSZ.PA"],
    ["EDF:FP", "EDF:FR", "EPA:EDF", "EDF.PA"],
    # --- Germany
    ["EOAN:GY", "EOAN:XE", "ETR:EOAN", "EOAN.DE"],
    ["RWE:GY", "RWE:XE", "ETR:RWE", "RWE.DE"],
    ["NDX1:GY", "NDX1:XE", "ETR:NDX1", "NDX1.DE"],
    # --- Denmark
    ["VWS:DC", "VWS:DK", "CPH:VWS", "VWS.CO"],
    # --- Finland
    ["FUM1V:FH", "FUM1V:FI", "HEL:FUM1V", "FOT.F"],
    # --- Austria
    ["VER:AV", "VER:AT", "VIE:VER", "VER.VI"],
    # --- Eastern Europe
    ["CEZ:CP", "BAACEZ:CZ", None, None],
    ["PGE:PW", "PGE:PL", "WSE:PGE", None],
    ["TPE:PW", "TPE:PL", "WSE:TPE", None],
    ["ENG:PW", "ENG:PL", "WSE:ENG", None],
    # --- Brazil
    ["LIGT3:BZ", "LIGT3:BR", "BVMF:LIGT3", "LIGT3.SA"],
])

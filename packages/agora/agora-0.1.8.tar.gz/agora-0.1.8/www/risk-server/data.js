var MASTER_POSITIONS = [
    {"security": "A2A IM EQUITY", "units": -1500000, "exposure": -1943494, "days": 0.09, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ABG SM EQUITY", "units": -290718, "exposure": -1625976, "days": 0.40, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ABG/P SM EQUITY", "units": 2150640, "exposure": 999114, "days": 0.24, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "BZJ4 INDEX", "units": -150, "exposure": -3335867, "days": 0.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "CESP6 BZ EQUITY", "units": -341125, "exposure": -4002759, "days": 0.43, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "CEZ CP EQUITY", "units": -138484, "exposure": -3966449, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "CIG US EQUITY", "units": 221058, "exposure": 1503194, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "COCE5 BZ EQUITY", "units": 127170, "exposure": 2080138, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "BZ EQUITY", "units": -100000, "exposure": -818958, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "CSMG3 BZ EQUITY", "units": -12075, "exposure": -193153, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "DRX LN EQUITY", "units": 250000, "exposure": 3190773, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "EDF FP EQUITY", "units": -93750, "exposure": -3706658, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "EDPR PL EQUITY", "units": 1098750, "exposure": 7313208, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ELP US EQUITY", "units": -114927, "exposure": -1506693, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ELPL4 BZ EQUITY", "units": 500000, "exposure": -1882283, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ENBR3 BZ EQUITY", "units": 10000, "exposure": 45351, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ENEL IM EQUITY", "units": 1125000, "exposure": 6363343, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ENG PW EQUITY", "units": 375000, "exposure": 2212284, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ENG SM EQUITY", "units": 57383, "exposure": 1744160, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "EOAN GY EQUITY", "units": -248750, "exposure": -4860130, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "EONR RX EQUITY", "units": 11500000, "exposure": 796696, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "EQTL3 BZ EQUITY", "units": 297500, "exposure": 2678730, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "FGR FP EQUITY", "units": 37500, "exposure": 2804745, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "FOT 5 P16.50 EQUITY", "units": -1000, "exposure": -1837955, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "FUM1V FH EQUITY", "units": -82500, "exposure": -1874305, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "GAM SM EQUITY", "units": 638750, "exposure": 6930420, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "GETI3 BZ EQUITY", "units": 252900, "exposure": 1759360, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "GETI4 BZ EQUITY", "units": -352900, "exposure": -2803089, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000}, 
    {"security": "IBJ4 INDEX", "units": 19, "exposure": 2698256, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "MOZ4 COMDTY", "units": 550, "exposure": 3559287, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "REE SM EQUITY", "units": -21525, "exposure": -1748629, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "RWE GY EQUITY", "units": -212500, "exposure": -8619738, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "RWE3 GY EQUITY", "units": 211608, "exposure": 6883452, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "SBS US EQUITY", "units": 285000, "exposure": 2639100, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "SBSP3 BZ EQUITY", "units": 133875, "exposure": 1243743, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "SSE LN EQUITY", "units": 128250, "exposure": 3139108, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "STM4 INDEX", "units": -19, "exposure": -2799238, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "TRPL4 BZ EQUITY", "units": 211500, "exposure": 2293631, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "VER AV EQUITY", "units": -343893, "exposure": -7069449, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "VIE FP EQUITY", "units": -100000, "exposure": -1977228, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "VWS DC EQUITY", "units": 56250, "exposure": 2259131, "days": 3.00, "beta": 0.95, "mkt_cap": 1000000000},
];

var FUNDAMENTAL_POSITIONS = [
    {"security": "A2A IM EQUITY", "units": -1500000, "exposure": -1943494, "days": 0.09, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ABG SM EQUITY", "units": -290718, "exposure": -1625976, "days": 0.40, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "ABG/P SM EQUITY", "units": 2150640, "exposure": 999114, "days": 0.24, "beta": 0.95, "mkt_cap": 1000000000},
    {"security": "BZJ4 INDEX", "units": -150, "exposure": -3335867, "days": 0.00, "beta": 0.95, "mkt_cap": 1000000000},
]

var GROSS_BY_REGION = {
    cols: [{id: "region", label: "Region", type: "string"},
           {id: "gross", label: "Gross Exposure", type: "number"}],
    rows: [
        {c: [{v: "Nth.Europe"}, {v: 1500000}]},
        {c: [{v: "Cnt.Europe"}, {v: 1000000}]},
        {c: [{v: "Sth.Europe"}, {v: 3000000}]},
        {c: [{v: "East.Europe"}, {v: 1000000}]},
        {c: [{v: "Nth.America"}, {v: 100000}]},
        {c: [{v: "Lat.Am."}, {v: 2000000}]} ],
};

var GROSS_BY_SECTOR = {
    cols: [{id: "sector", label: "Sector", type: "string"},
           {id: "gross", label: "Gross Exposure", type: "number"}],
    rows: [
        {c: [{v: "Regulated"}, {v: 100000}]},
        {c: [{v: "Vertically Integrated"}, {v: 3000000}]},
        {c: [{v: "IPP"}, {v: 1000000}]},
        {c: [{v: "Infra"}, {v: 3000000}]},
        {c: [{v: "Renewables"}, {v: 5000000}]},
        {c: [{v: "Oil"}, {v: 1000000}]} ],
};

var VAR_BY_REGION = {
    cols: [{id: "region", label: "Region", type: "string"},
           {id: "var", label: "VaR", type: "number"}],
    rows: [
        {c: [{v: "Nth.Europe"}, {v: 1500000}]},
        {c: [{v: "Cnt.Europe"}, {v: 1000000}]},
        {c: [{v: "Sth.Europe"}, {v: 3000000}]},
        {c: [{v: "East.Europe"}, {v: 1000000}]},
        {c: [{v: "Nth.America"}, {v: 100000}]},
        {c: [{v: "Lat.Am."}, {v: 2000000}]} ],
};

var VAR_BY_SECTOR = {
    cols: [{id: "sector", label: "Sector", type: "string"},
           {id: "var", label: "VaR", type: "number"}],
    rows: [
        {c: [{v: "Regulated"}, {v: 100000}]},
        {c: [{v: "Vertically Integrated"}, {v: 3000000}]},
        {c: [{v: "IPP"}, {v: 1000000}]},
        {c: [{v: "Infra"}, {v: 3000000}]},
        {c: [{v: "Renewables"}, {v: 5000000}]},
        {c: [{v: "Oil"}, {v: 1000000}]} ],
};

var STRESS_SCENARIOS = {
    scenarios: ["Lehman Default", "Fukushima", "Sovreing Crisis"],
    positions: [
        {security: "A2A IM EQUITY", exposure: -1943494, "Lehman Default": 0.01, "Fukushima": -0.02, "Sovreing Crisis": 0.03},
        {security: "ABG SM EQUITY", exposure: -1625976, "Lehman Default": 0.01, "Fukushima": -0.02, "Sovreing Crisis": 0.03},
        {security: "ABG/P SM EQUITY", exposure: 999114, "Lehman Default": 0.01, "Fukushima": -0.02, "Sovreing Crisis": 0.03},
    ],
};


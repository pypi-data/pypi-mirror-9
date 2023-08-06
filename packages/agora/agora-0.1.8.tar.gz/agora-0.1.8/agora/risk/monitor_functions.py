###############################################################################
#
#  Agora Portfolio & Risk Management System
#
#  Description: risk monitoring
#
#  File Created: 01 Jan 2015
#  Author: Carlo Sbraccia
#
###############################################################################

import math

CCS_STYLE_BLOCK = """
<style>
    th, td {
        text-align: right;
    }
    .risk_table {
        margin-left: auto;
        margin-right: auto;
        border: 1px solid #585858;
        border-collapse: collapse;
        background-color: #000000;
        color: #FFFFFF;
        padding-right: 5px;
        font-family: "Segoe UI Bold", "Arial";
        font-size: 8pt;
        font-weight: bold;
        -ms-font-feature-settings: "ss01";
    }
    .risk_tab_header {
        color: #FF9900;
        font-size: 9pt;
        font-weight: bold;
        background-repeat:no-repeat;
        background: #555555;
    }
    .alt {
        background-color: #222222;
    }
    .yellow {
        color: #3366FF;
        background-color: #FFFF66;
    }
    .amber {
        color: #0039E6;
        background-color: #FF7E00;
    }
    .red {
        color: #000000;
        background-color: #FF0000;
    }
</style>
"""

################################################################################
##  monitorSingleNameExposure
##------------------------------------------------------------------------------
def monitorSingleNameExposure( weight ):
    color = "plain"
    if weight >= 0.8*15.0:
        color = "yellow"
    if weight >= 0.9*15.0:
        color = "amber"
    if weight >= 15.0:
        color = "red"
    return color

################################################################################
##  monitorSingleNameLiquidity
##------------------------------------------------------------------------------
def monitorSingleNameLiquidity( pct_of_max_vol ):
    color = "plain"
    if pct_of_max_vol >= 80.0:
        color = "yellow"
    if pct_of_max_vol >= 90.0:
        color = "amber"
    if pct_of_max_vol >= 100.0:
        color = "red"
    return color

################################################################################
##  monitorOwnership
##------------------------------------------------------------------------------
def monitorOwnership( ownership, exchange ):
    color = "plain"
    if exchange == "BZ":
        return color

    if exchange == "LN":
        if ownership <= -0.8*0.2 or ownership >= 0.8*3.0:
            color = "yellow"
        if ownership <= -0.9*0.2 or ownership >= 0.9*3.0:
            color = "amber"
        if ownership <= -0.2 or ownership >= 3.0:
            color = "red"
    else:
        if ownership <= -0.8*0.2 or ownership >= 0.8*5.0:
            color = "yellow"
        if ownership <= -0.9*0.2 or ownership >= 0.9*5.0:
            color = "amber"
        if ownership <= -0.2 or ownership >= 5.0:
            color = "red"
    return color

################################################################################
##  monitorNetExposure
##------------------------------------------------------------------------------
def monitorNetExposure( net_exposure ):
    color = "plain"
    if math.fabs( net_exposure ) >= 0.8*0.50:
        color = "yellow"
    if math.fabs( net_exposure ) >= 0.9*0.50:
        color = "amber"
    if math.fabs( net_exposure ) >= 0.50:
        color = "red"
    return color

################################################################################
##  monitorGrossExposure
##------------------------------------------------------------------------------
def monitorGrossExposure( grs_exposure ):
    color = "plain"
    if grs_exposure >= 0.8*3.0:
        color = "yellow"
    if grs_exposure >= 0.9*3.0:
        color = "amber"
    if grs_exposure >= 3.0:
        color = "red"
    return color

################################################################################
##  monitorCommodExposure
##------------------------------------------------------------------------------
def monitorCommodExposure( com_exposure ):
    color = "plain"
    if math.fabs( com_exposure ) >= 0.8 / 3.0:
        color = "yellow"
    if math.fabs( com_exposure ) >= 0.9 / 3.0:
        color = "amber"
    if math.fabs( com_exposure ) >= 1.0 / 3.0:
        color = "red"
    return color

################################################################################
##  monitorDailyVaR
##------------------------------------------------------------------------------
def monitorDailyVaR( var_pct ):
    color = "plain"
    if var_pct >= 0.8*0.03:
        color = "yellow"
    if var_pct >= 0.9*0.03:
        color = "amber"
    if var_pct >= 0.03:
        color = "red"
    return color

################################################################################
##  monitorDaysToExpiration
##------------------------------------------------------------------------------
def monitorDaysToExpiration( days_to_exp ):
    color = "plain"
    if days_to_exp <= 5:
        color = "yellow"
    if days_to_exp <= 2:
        color = "amber"
    if days_to_exp <= 1:
        color = "red"
    return color
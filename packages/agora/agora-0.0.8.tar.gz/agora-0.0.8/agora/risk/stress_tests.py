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

from Agora.LIB_PortfolioFns import Option, createUnique, Security
from Agora.LIB_HistPricesFns import GetProxy

__all__ = [ "StressTestReport" ]

PORTTAG = "Portfolio"

################################################################################
##  StressTestReport
##------------------------------------------------------------------------------
def StressTestReport( pd, scenarios, aum, fund ):
    positions = []
    for sec, qty in fund.positions.iteritems():

        if isinstance( sec, Option ):
            qty *= sec.delta( pd )
            sec  = sec.underlying

        if sec.name.endswith( "INDEX" ) or sec.name.endswith( "COMDTY" ):
            try:
                proxysec, proxyccy = GetProxy( sec.underlying.name, 0 )
                sec = createUnique( proxysec, proxyccy, Security )
            except KeyError:
                # --- proxy not found: try without
                pass

        positions.append( ( sec, qty ) )

    report = {
        "scenarios": [],
        "rows": { sec.name: { "pos": qty*sec.lastUSD( pd ) / aum }
                  for sec, qty in positions if not sec.isccy },
        "portfolio": {},
    }

    for name, sd, ed in scenarios:
        scenario = RunScenario( positions, aum, pd, sd, ed )
        report["scenarios"].append( name )
        report["portfolio"][name] = scenario.pop( PORTTAG )
        for sec, data in scenario.iteritems():
            ret = data["Change"]
            pnl = data["PnL"]
            report["rows"][sec].update( { name: { "pnl": pnl, "chg": ret } } )

    return report

################################################################################
##  RunScenario
##------------------------------------------------------------------------------
def RunScenario( positions, nav, pd, sd, ed ):
    rep, tot = {}, 0.0
    for sec, qty in positions:
        px   = sec.lastUSD( pd )
        px_i = sec.lastUSD( sd )
        px_f = sec.lastUSD( ed )
        ret  = ( px_f - px_i ) / px_i
        pnl  = qty*px*ret/nav
        tot += pnl
        if not sec.isccy:
            rep[sec.name] = { "Change" : ret, "PnL" : pnl }

    rep[PORTTAG] = { "Change" : None, "PnL" : tot }

    return rep

def FormatReport( report, aum, fout ):

    names  = report[0][2:]

    print >> fout, "<table><thead>"
    print >> fout, "<tr><th rowspan=2>Security</th>" + \
                       "<th rowspan=2>Position</th>" + \
                       "<th colspan=2>%s</th>"*len( names ) % tuple( names ) + "</tr>"
    print >> fout, "<tr>" + "<th>Change</th><th>P&L</th>"*len( names ) + "</tr>"
    print >> fout, "</thead><tbody>"

    for row in report[1:]:
        if row[1] is None:
            record = """<tr><td style="width:150px;">{0:>s}</td>
                            <td style="width:80px;"></td>""".format( row[0] )
        else:
            pos = 100.0 * row[1] / aum
            record = """<tr><td style="width:150px;">{0:>s}</td>
                            <td style="width:70px;">{1:6,.2f}%</td>""".format( row[0], pos )

        for chg, pnl in row[2:]:
            if chg is None:
                record += """<td style="width:80px;"></td>
                             <td style="width:50px;">{0:6,.2f}%</td>""".format( pnl*100.0 )
            else:
                record += """<td style="width:80px;">{0:6,.2f}%</td>
                             <td style="width:50px;">{1:6,.2f}%</td>""".format( chg*100.0, pnl*100.0 )

        record += "</tr>"

        print >> fout, record

    return fout

################################################################################
##  main
##------------------------------------------------------------------------------
def main():
    from Snail.LIB_Datatypes import Date
    from Snail.LIB_CurveFns import Interpolate
    from Snail.LIB_DateFns import DateRuleApply
    from Snail.LIB_PortfolioIOFns import LoadPositionsFromFtp
    from Snail.CFG_FundParameters import FTPHOST, FTPUSER, FTPPASSWD
    from Snail.CFG_FundParameters import NAVCRV

    pd = Date( 2013, 11, 12 )

    # --- interest rate cenarios (USGG10YR)
    scenarios = [
        ( "IR1", DateRuleApply( Date( 2008, 10, 14 ), "-5b" ), Date( 2008, 10, 14 ) ), # +0.5744
        ( "IR2", DateRuleApply( Date( 2008, 11, 20 ), "-5b" ), Date( 2008, 11, 20 ) ), # -0.8394
        ( "IR3", DateRuleApply( Date( 2008, 12, 18 ), "-5b" ), Date( 2008, 12, 18 ) ), # -0.5231
        ( "IR4", DateRuleApply( Date( 2009,  5, 27 ), "-5b" ), Date( 2009,  5, 27 ) ), # +0.5469
        ( "IR5", DateRuleApply( Date( 2011,  8,  4 ), "-5b" ), Date( 2011,  8,  4 ) ), # -0.5427
        ( "IR6", DateRuleApply( Date( 2013,  6, 25 ), "-5b" ), Date( 2013,  6, 25 ) ), # +0.4229
    ]

    nav  = Interpolate( NAVCRV, pd )
    fund = LoadPositionsFromFtp( host       = FTPHOST,
                                 user       = FTPUSER,
                                 passwd     = FTPPASSWD,
                                 date       = pd,
                                 portFilter = "CFP Equity Master Fund Limited" )

    return StressTestReport( pd, scenarios, nav, fund )

if __name__ == "__main__":
    report = main()
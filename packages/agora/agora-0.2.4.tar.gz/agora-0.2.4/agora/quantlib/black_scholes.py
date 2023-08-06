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

from numpy import where, vectorize
from numpy import log as np_log, sqrt as np_sqrt, exp as np_exp
from math import (log as m_log, sqrt as m_sqrt,
                  exp as m_exp, expm1 as m_expm1, erf as m_erf, pi as m_pi)

from scipy.optimize import bisect

__all__ = ["opt_BS", "opt_BAW", "opt_JZ", "quick_delta", "implied_vol"]

# --- local variables and functions
invsqrt2 = 1.0 / m_sqrt(2.0)

m_ncdf = lambda x: 0.5*(1.0 + m_erf(x*invsqrt2))
v_ncdf = vectorize(m_ncdf, otypes=[float])


# -----------------------------------------------------------------------------
def opt_BS(opt_type, spot, strike, vol, term, rd, rf, ret_type="PREMIUM"):
    """
    Description:
        Black-Scholes option price and greeks for different european option
        types.
        Black76 formula for futures is retrived by setting rd = rf = r.
    Inputs:
        opt_type - option type (CALL, PUT). Only first letter is used.
        spot     - current spot price
        strike   - strike of the option
        vol      - price volatility (standard deviation of log returns)
        term     - time to expiration (units must be consistent with what is
                   used for vol, rd, rf)
        rd       - domestic risk-free interest rate
        rf       - foreign risk-free interest rate (or dividend yield)
        ret_type - quantity to be computed (PREMIUM, DELTA). Only first letter
                   is used.
    Returns:
        A float as per ret_type.
    """
    # --- convert string arguments to upper-case
    opt_type = opt_type[0].upper()
    ret_type = ret_type[0].upper()

    # --- precompute as much as possible
    volsqrtt = vol*np_sqrt(term)

    # --- early return if possible
    if volsqrtt <= 0.00025:
        # --- either volatility is zero or very small or we are extremely close
        #     to expiration. Return based on intrinsic value.

        # --- Calls
        if opt_type == "C":
            if ret_type == "P":
                moneyness = spot*np_exp((rd - rf)*term) - strike
                return m_exp(-rd*term)*where(moneyness <= 0.0, 0.0, moneyness)
            elif ret_type == "D":
                otm = spot*np_exp((rd - rf)*term) <= strike
                return where(otm, 0.0, np_exp(-rf*term))
            else:
                NameError("Unrecognized return type, {0:s}".format(ret_type))

        # --- Puts
        elif opt_type == "P":
            if ret_type == "P":
                moneyness = strike - spot*np_exp((rd - rf)*term)
                return m_exp(-rd*term)*where(moneyness <= 0.0, 0.0, moneyness)
            elif ret_type == "D":
                otm = strike <= spot*np_exp((rd - rf)*term)
                return where(otm, 0.0, -np_exp(-rf*term))
            else:
                NameError("Unrecognized return type, {0:s}".format(ret_type))
        else:
            raise NameError("Unrecognized option type, {0:s}".format(opt_type))

    # --- calculate according to Black-Scholes
    d1 = (np_log(spot / strike) + (rd - rf + 0.5*vol*vol)*term) / volsqrtt

    # --- Calls
    if opt_type == "C":
        if ret_type == "P":
            return (np_exp(-rf*term)*spot*v_ncdf(d1) -
                    np_exp(-rd*term)*strike*v_ncdf(d1 - volsqrtt))
        elif ret_type == "D":
            return np_exp(-rf*term)*v_ncdf(d1)
        else:
            NameError("Unrecognized return type, {0:s}".format(ret_type))

    # --- Puts
    elif opt_type == "P":
        if ret_type == "P":
            return (np_exp(-rd*term)*strike*v_ncdf(volsqrtt - d1) -
                    np_exp(-rf*term)*spot*v_ncdf(-d1))
        elif ret_type == "D":
            return -np_exp(-rf*term)*v_ncdf(-d1)
        else:
            NameError("Unrecognized return type, {0:s}".format(ret_type))

    else:
        raise NameError("Unrecognized option type, {0:s}".format(opt_type))


# -----------------------------------------------------------------------------
def opt_BAW(opt_type, spot, strike, vol, term, rd, rf):
    """
    Description:
        Barone-Adesi Whaley approximation for american options (premium only).
        The formula for futures is retrived by setting rd = rf = r.
    Inputs:
        opt_type - option type (CALL, PUT). Only first letter is used.
        spot     - current spot price
        strike   - strike of the option
        vol      - price volatility (standard deviation of log returns)
        term     - time to expiration (units must be consistent with what is
                   used for vol, rd, rf)
        rd       - domestic risk-free interest rate
        rf       - foreign risk-free interest rate (or dividend yield)
    Returns:
        A float.
    """
    # --- convert string arguments to upper-case
    opt_type = opt_type[0].upper()

    # --- precompute as much as possible
    volsq = vol*vol

    if term == 0.0 or volsq <= 0.00005:
        disc = m_exp(-rd*term)
        if opt_type == "C":
            return max(max(spot - strike, 0.0),
                       max(spot*m_exp((rd - rf)*term) - strike, 0.0)*disc)
        elif opt_type == "P":
            return max(max(strike - spot, 0.0),
                       max(strike - spot*m_exp((rd - rf)*term), 0.0)*disc)
        else:
            raise NameError("Unrecognized option type, {0:s}".format(opt_type))

    h = - m_expm1(-rd*term)
    a = 2.0*rd / volsq
    # this is actually -(beta-1) using Hull's notation
    b = 1.0 - 2.0*(rd - rf) / volsq

    if opt_type == "C":
        g = 0.5*(b + m_sqrt(b*b + 4.0*a / h))
        ss = critical_price_BAW(opt_type, strike, vol, term, rd, rf, g)

        if spot < ss:
            # --- below critical price: option should not be exercised
            d1 = ((m_log(ss / strike) +
                  (rd - rf + 0.5*volsq)*term) / (vol*m_sqrt(term)))
            A = ss / g * (1.0 - m_exp(-rf*term)*m_ncdf(d1))

            return (A*(spot / ss)**g +
                    opt_BS("C", spot, strike, vol, term, rd, rf))
        else:
            # --- option should be exercised
            return spot - strike

    elif opt_type == "P":
        g = 0.5*(b - m_sqrt(b*b + 4.0*a / h))
        ss = critical_price_BAW(opt_type, strike, vol, term, rd, rf, g)

        if spot > ss:
            # --- above critical price: option should not be exercised
            d1 = ((m_log(ss / strike) +
                  (rd - rf + 0.5*volsq)*term) / (vol*m_sqrt(term)))
            A = - ss / g * (1.0 - m_exp(-rf*term)*m_ncdf(-d1))

            return (A*(spot / ss)**g +
                    opt_BS("P", spot, strike, vol, term, rd, rf))
        else:
            # --- option should be exercised
            return strike - spot

    else:
        raise NameError("Unrecognized option type, {0:s}".format(opt_type))


# -----------------------------------------------------------------------------
def critical_price_BAW(opt_type, K, vol, term, rd, rf, g):
    """
    Auxiliary function used by the Barone-Adesi Whaley approximation for
    american options.
    """
    # --- pre-calculate constant terms
    drift = (rd - rf + 0.5*vol*vol)*term
    volsqrtt = vol*m_sqrt(term)
    invden = 1.0 / volsqrtt
    disc_rd = m_exp(-rd*term)
    disc_rf = m_exp(-rf*term)

    if opt_type == "C":
        def error(ss):
            d1 = (m_log(ss / K) + drift)*invden
            bs = disc_rf*ss*m_ncdf(d1) - disc_rd*K*m_ncdf(d1 - volsqrtt)
            return bs + (1.0 - disc_rf*m_ncdf(d1)) * ss / g - (ss - K)

        # --- early return if possible
        if error(2.0*K) > 0.0:
            return 2.0*K
        else:
            return bisect(error, K, 2.0*K, xtol=0.0005, full_output=False)

    else:
        def error(ss):
            d1 = (m_log(ss / K) + drift)*invden
            bs = disc_rd*K*m_ncdf(volsqrtt - d1) - disc_rf*ss*m_ncdf(-d1)
            return bs - (1.0 - disc_rf*m_ncdf(-d1)) * ss / g - (K - ss)

        return bisect(error, 0.0005, K, xtol=0.0005, full_output=False)


# -----------------------------------------------------------------------------
def opt_JZ(opt_type, spot, strike, vol, term, rd, rf):
    """
    Description:
        Ju-Zhong approximation for american options (premium only).
        The formula for futures is retrived by setting rd = rf = r.
    Inputs:
        opt_type - option type (CALL, PUT). Only first letter is used.
        spot     - current spot price
        strike   - strike of the option
        vol      - price volatility (standard deviation of log returns)
        term     - time to expiration (units must be consistent with what is
                   used for vol, rd, rf)
        rd       - domestic risk-free interest rate
        rf       - foreign risk-free interest rate (or dividend yield)
    Returns:
        A float.
    """
    # --- convert string arguments to upper-case
    opt_type = opt_type[0].upper()

    # --- precompute as much as possible
    volsq = vol*vol

    if term == 0.0 or volsq <= 0.00005:
        disc = m_exp(-rd*term)
        if opt_type == "C":
            return max(max(spot - strike, 0.0),
                       max(spot*m_exp((rd - rf)*term) - strike, 0.0)*disc)
        elif opt_type == "P":
            return max(max(strike - spot, 0.0),
                       max(strike - spot*m_exp((rd - rf)*term), 0.0)*disc)
        else:
            raise NameError("Unrecognized option type, {0:s}".format(opt_type))

    h = -m_expm1(-rd*term)
    a = 2.0*rd / volsq
    # this is actually -(beta-1) using Hull's notation
    b = 1.0 - 2.0*(rd - rf) / volsq

    if opt_type == "C":
        g = 0.5*(b + m_sqrt(b*b + 4.0*a / h))
        ss = critical_price_BAW(opt_type, strike, vol, term, rd, rf, g)

        if spot < ss:
            # --- below critical price: option should not be exercised
            rdf = m_exp(-(rd - rf)*term) / rd
            vsqt = vol*m_sqrt(term)

            hA = ss - strike - opt_BS("C", ss, strike, vol, term, rd, rf)
            d1 = (m_log(ss / strike) + (rd - rf + 0.5*volsq)*term) / vsqt

            gp = - a / (h*h*m_sqrt(b*b + 4.0*a / h))
            dV = (strike*m_ncdf(d1 - vsqt) - rf*ss*m_ncdf(d1)*rdf +
                  0.5*ss*m_exp(-0.5*d1*d1)*volsq*rdf / vsqt / m_sqrt(2.0*m_pi))

            dn = 1.0 / (2.0*g - b)
            c1 = 0.5*(1.0 - h)*a*gp*dn
            c2 = -(1.0 - h)*a*dn*(dV / hA + 1.0 / h + gp*dn)

            lns = m_log(spot / ss)
            chi = c1*lns*lns + c2*lns

            return (hA*(spot / ss)**g / (1.0 - chi) +
                    opt_BS("C", spot, strike, vol, term, rd, rf))
        else:
            # --- option should be exercised
            return spot - strike

    elif opt_type == "P":
        g = 0.5*(b - m_sqrt(b*b + 4.0*a / h))
        ss = critical_price_BAW(opt_type, strike, vol, term, rd, rf, g)

        if spot > ss:
            # --- above critical price: option should not be exercised
            rdf = m_exp(-(rd - rf)*term) / rd
            vsqt = vol*m_sqrt(term)

            hA = strike - ss - opt_BS("P", ss, strike, vol, term, rd, rf)
            d1 = (m_log(ss / strike) + (rd - rf + 0.5*volsq)*term) / vsqt

            gp = a / (h*h*m_sqrt(b*b + 4.0*a / h))
            dV = (rf*ss*m_ncdf(-d1)*rdf - strike*m_ncdf(vsqt - d1) +
                  0.5*ss*m_exp(-0.5*d1*d1)*volsq*rdf / vsqt / m_sqrt(2.0*m_pi))

            dn = 1.0 / (2.0*g - b)
            c1 = 0.5*(1.0 - h)*a*gp*dn
            c2 = -(1.0 - h)*a*dn*(dV / hA + 1.0 / h + gp*dn)

            lns = m_log(spot / ss)
            chi = c1*lns*lns + c2*lns

            return (hA*(spot / ss)**g / (1.0 - chi) +
                    opt_BS("P", spot, strike, vol, term, rd, rf))
        else:
            # --- option should be exercised
            return strike - spot

    else:
        raise NameError("Unrecognized option type, {0:s}".format(opt_type))


##-----------------------------------------------------------------------------
def quick_delta(spot, strike, vol, term):
    """
    Description:
        Quick-Delta is a measure of moneyness (from 0 to 1) and is an
        approximation to the delta of a put option.
    Inputs:
        spot   - current spot price
        strike - strike of the option
        vol    - price volatility (stanard deviation of log returns)
        term   - time to expiration (units must be consistent with vol, rd, rf)
    """
    if term > 0.0:
        return m_ncdf(np_log(strike / spot) / (vol*np_sqrt(term)))
    else:
        return 1.0 if spot < strike else 0.0


##-----------------------------------------------------------------------------
def implied_vol(opt_type, premium, spot, strike, term, rd, rf,
                american=False, pricer=None, vol_min=0.0, vol_max=2.5):
    """
    Description:
        Computes the implied Black-Scholes volatility given option parameters
        and price.
        For american options, by default it uses the Barone-Adesi Whaley
        approximation (different pricers can be specified).
    Inputs:
        opt_type - option type (CALL, PUT). Only first letter is used.
        premium  - the option premium
        spot     - current spot price
        strike   - strike of the option
        term     - time to expiration (units must be consistent with what is
                   used for vol, rd, rf)
        rd       - domestic risk-free interest rate
        rf       - foreign risk-free interest rate (or dividend yield)
        american - if True, it uses the BAW pricer (unless a different pricer
                   is indicated)
        pricer   - the pricer to use for american options
        vol_min  - min volatility allowed (used for iterative root finding)
        vol_max  - max volatility allowed (used for iterative root finding)
    Returns:
        The implied volatility
    """
    if american:
        if pricer is None:
            pricer = opt_BAW

        def error(vol):
            return premium - pricer(opt_type, spot, strike, vol, term, rd, rf)

        if error(vol_min) == 0.0:
            # --- no extrinsic value: IV is defined as the largest vol such
            #     that the option still has no extrinsic value
            def error(vol):
                return (1.e-6 + premium -
                        pricer(opt_type, spot, strike, vol, term, rd, rf))

    else:
        def error(vol):
            return premium - opt_BS(opt_type, spot, strike, vol, term, rd, rf)

    return bisect(error, vol_min, vol_max, xtol=0.0005, full_output=False)

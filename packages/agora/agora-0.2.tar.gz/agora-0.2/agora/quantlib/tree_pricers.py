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

from agora.quantlib.black_scholes import opt_BS

from math import exp as m_exp, sqrt as m_sqrt
from numpy import exp, where

import numpy as np

__all__ = ["opt_BT"]


# -----------------------------------------------------------------------------
def opt_BT(opt_type, spot, strike,
           vol, term, rd, rf, style="EUROPEAN", n_steps=510):
    """
    Description:
        Black-Scholes option pricer based on Binomial Tree discretization of
        time.
        It can price both european and american exercise-style options.
        Black76 formula for futures is retrived by setting rd = rf = r.
    Inputs:
        opt_type - option type (CALL, PUT). Only first letter is used.
        spot     - current spot price
        strike   - strike of the option
        vol      - price volatility (standard deviation of log returns)
        term     -  time to expiration (units must be consistent with what is
                   used for vol, rd, rf)
        rd       - domestic risk-free interest rate
        rf       - foreign risk-free interest rate (or dividend yield)
        style    - exercise style (EUROPEAN, AMERICAN). Only first letter
                   is used.
        n_steps  - number of discretization time-steps on a per-year basis
                   (default is 510 steps per year, about 2 per biz-day)
    Returns:
        The option's fair value
    """
    # --- convert string arguments to upper-case
    opt_type = opt_type[0].upper()
    style = style[0].upper()

    # --- Calls
    if opt_type == "C":
        payoff = np.vectorize(lambda s: max(s - strike, 0.0), otypes=[float])
    # --- Puts
    elif opt_type == "P":
        payoff = np.vectorize(lambda s: max(strike - s, 0.0), otypes=[float])
    else:
        raise NameError("Unrecognized option type, {0:s}".format(opt_type))

    # --- convert n_steps to total number of steps for the binomial tree
    n_steps = int(n_steps*term)

    dt = term / float(n_steps)
    df = m_exp(-rd*dt)

    drift = (rd - rf - 0.5*vol*vol)
    volsqrtdt = vol*m_sqrt(dt)

    # --- european exercise
    if style == "E":
        for k in range(n_steps, -1, -1):
            if k == n_steps:
                opt = payoff(spot*exp(drift*k*dt +
                                      volsqrtdt*np.linspace(-k, k, k+1)))
            else:
                # --- PV of the one-step-ahead expected value
                opt = df*0.5*(opt[1:] + opt[:-1])

        return opt[0]

    # --- american exercise (it uses a european option as control variate
    #     to reduce error)
    elif style == "A":
        for k in range(n_steps, -1, -1):
            if k == n_steps:
                opt = payoff(spot*exp(drift*k*dt +
                                      volsqrtdt*np.linspace(-k, k, k+1)))
                euro = opt
            else:
                # --- intrinsic value
                intrinsic = payoff(spot*exp(drift*k*dt +
                                            volsqrtdt*np.linspace(-k, k, k+1)))

                # --- continuation value: PV of the one-step-ahead
                #     expected value
                cont = df*0.5*(opt[1:] + opt[:-1])

                # --- option's value is the best of the intrinsic and
                #     continuation values
                opt = where(cont > intrinsic, cont, intrinsic)

                # --- european option (used for control variate)
                euro = df*0.5*(euro[1:] + euro[:-1])

        # --- assume error for the european option can be used as a correction
        #     for the american one. However, always enforce that fair value is
        #     at least the intrinsic value.
        exact_bs = opt_BS(opt_type, spot, strike, vol, term, rd, rf)
        return max(opt[0] + exact_bs - euro[0], payoff(spot))

    else:
        raise NameError("Unrecognized exercise style, {0:s}".format(style))

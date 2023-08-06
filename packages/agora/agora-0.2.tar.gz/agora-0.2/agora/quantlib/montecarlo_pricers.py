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

from numpy.polynomial import polynomial, laguerre, hermite_e

import numpy as np
import math

__all__ = ["MC_vanilla", "MC_american"]


##-----------------------------------------------------------------------------
def MC_vanilla(prices, payoff, rd, rf, term, bstrap=False):
    """
    Description:
        Monte-Carlo pricer for payoffs that only depend on terminal (marginal)
        distribution of prices (european style exercise).
    Inputs:
        prices - ensemble of terminal prices
        payoff - scalar payoff function
        term   - time to expiration (units must be consistent with rd and rf)
        rd     - domestic risk-free interest rate
        rf     - foreign risk-free interest rate (or dividend yield)
        bstrap - if Trues, use bootstrap resampling to get better estimate of
                 monte-carlo error.
                 NB: current implementation seems to improve estimates very
                 little...
    Returns:
         A tuple of floats with premium and its error.
    """
    # --- vectorize payoff function
    payoff = np.vectorize(payoff, otypes=[float])

    # --- discount factor
    df = math.exp(-rd*term)

    # --- apply payoff to price paths
    samples = payoff(prices)

    if bstrap:
        n = samples.shape[0]
        bstrap_samples = []
        for _ in range(min(n, 1000)):
            idxs = np.random.random_integers(0, n - 1, n)
            bstrap_samples.append(samples[idxs].mean())
        return df*np.mean(bstrap_samples), df*np.std(bstrap_samples)
    else:
        return (df*samples.mean(),
                df*samples.std() / math.sqrt(samples.shape[0] - 1.0))


##-----------------------------------------------------------------------------
def MC_american(paths, payoff, term, rd, rf,
                basis="POLY", full_distr=False, **kwds):
    """
    Description:
        Monte-Carlo pricer for payoffs with american-style exercise.
    Inputs:
        paths      - ensemble of prices paths
        payoff     - scalar payoff function
        term       - time to expiration (units must be consistent with rd, rf)
        rd         - domestic risk-free interest rate
        rf         - foreign risk-free interest rate (or dividend yield)
        basis      - basis set used to fit extrinsic continuation value: choose
                     among "POLY", "LAGUERRE", "HERMITE"
        full_distr - if True, returns the whole distribution, rather than the
                     mean
        kwds       - extra named arguments used for pricing an equivalent
                     european option for variance reduction.
                     Required parameters are:
                        - opt_type - option type (CALL, PUT)
                        - spot     - current spot price
                        - strike   - strike of the option
                        - vol      - price volatility (standard deviation of
                                     log returns)
    Returns:
        A tuple of floats (premium and its error) or a numpy.array if
        full_distr is True.
    """
    # --- vectorize payoff function
    payoff = np.vectorize(payoff, otypes=[float])

    # --- generate function used to fit the extrinsic continuation value
    if basis.upper() == "POLY":
        def extrcontval(x, y, deg):
            # --- Vandermonde matrix of powers of x
            B = polynomial.polyvander(x, deg).T
            return np.dot(B.T,
                          np.dot(np.linalg.pinv(np.dot(B, B.T)),
                                 np.dot(B, y)))

    elif basis.upper() == "LAGUERRE":
        def extrcontval(x, y, deg):
            # --- Vandermonde matrix of weighted Laguerre polynomials of
            #     x plus constant
            wx = np.exp(-0.5*x)
            B = np.vstack((np.ones_like(x), wx*laguerre.lagvander(x, deg).T))
            return np.dot(B.T,
                          np.dot(np.linalg.pinv(np.dot(B, B.T)),
                                 np.dot(B, y)))

    elif basis.upper() == "HERMITE":
        def extrcontval(x, y, deg):
            # --- Vandermonde matrix of weighted Hermite polynomials of
            #     x plus constant
            wx = np.exp(-0.5*x*x)
            B = np.vstack((np.ones_like(x),
                           wx*hermite_e.hermevander(x, deg).T))
            return np.dot(B.T,
                          np.dot(np.linalg.pinv(np.dot(B, B.T)),
                                 np.dot(B, y)))

    else:
        NameError("Unrecognized basis {0:s}".format(basis))

    # --- index of last time step
    last = paths.shape[0] - 1

    # --- one-step discount factor
    df = math.exp(-rd * term / float(last + 1))

    # --- walk backward: at each step cv contains the PV at that step of
    #     the cashflows conditional to not having exercised the option yet.
    for k in range(last, 0, -1):
        if k == last:
            # --- at expiration the continuation value is zero: always
            #     exercise the option if ITM
            cf = payoff(paths[k,:])
        else:
            # --- cash-flow at current time-step:
            #     1) if a path is OTM keep the option: current cash-flow is
            #        the PV of the one step ahead cash-flow.
            #     2) if a path is ITM:
            #        2.1) if expected continuation value is more than
            #             intrinsic keep the option: current cash-flow is
            #             the PV of the one step ahead cash-flow.
            #        2.2) otherwise exercise: current cash-flow is the
            #             intrinsic value.

            # --- start by calculating PV of the one step ahead cash-flow
            cf *= df

            # --- intrinsic value at current step
            intrinsic = payoff(paths[k,:])

            # --- indexes of in the money paths
            itm = np.nonzero(np.ravel(intrinsic > 0.0))[0]

            # --- for the ITM paths (if any), compare expected conditional
            #     continuation value to the intrinsic value
            if len(itm):
                # --- fit extrinsic continuation value
                x = paths[k,itm]
                y = cf[itm] - intrinsic[itm]

                # --- scale x to improve fit's condition number
                xmin, xmax = x.min(), x.max()
                if xmax > xmin:
                    x = (x - xmin) / (xmax - xmin)

                degree  = max(1, int(math.log(len(itm), 4)))
                cf[itm] = np.where(extrcontval(x, y, degree) > 0.0,
                                   cf[itm], intrinsic[itm])

    # --- try to get extra parameters needed to use the exact price of an
    #     equivalent european option as control variate
    try:
        opt_type = kwds["opt_type"]
        spot = kwds["spot"]
        strike = kwds["strike"]
        vol = kwds["vol"]

        # --- PV of payoffs for the european option
        euro_mc = math.exp(-rd*term)*payoff(paths[-1,:])
        euro_bs = opt_BS(opt_type, spot, strike, vol, term, rd, rf)

        # --- determine the coefficient that minimizes the variance of the
        #     estimate
        covmat = np.cov(cf, euro_mc)
        coeff = covmat[0,1] / covmat[1,1]    

        cf += coeff*(euro_bs - euro_mc)

    except KeyError:
        pass

    if full_distr:
        return cf
    else:
        return cf.mean(), cf.std() / math.sqrt(cf.shape[0] - 1.0)

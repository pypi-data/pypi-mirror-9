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

from agora.econometrics.optimization import (QuickMin,
                                             ConvergenceError, Hessian_FD_g)

from math import log as m_log, sqrt as m_sqrt, pi as m_pi

import numpy as np
import scipy.optimize as scipyopt

__all__ = ["Garch11", "IGarch11", "Garch11_CondVol"]

EPS = 1.e-6
MAXITER = 500

################################################################################
class QuickMinGarch11(QuickMin):
    def enforce_constraints(self):
        # --- parameters are positive
        self.pos = np.where(self.pos > EPS, self.pos, EPS)
        # --- domain constratint
        if self.pos[1] + self.pos[2] >= 1.0:
            self.pos[1:] /= (self.pos[1] + self. pos[2] + 1.e-2)


# -----------------------------------------------------------------------------
def Garch11(ret, skip=10, guess=None, verbose=False):
    """
    Description:
        ...
    Inputs:
        x - ...
    Returns:
        ...
    """
    if guess is None:
        guess = np.array([1.e-4, 0.15, 0.80])

    esq = (ret - ret.mean())**2
    args = (esq, skip)
    bounds = ( ( EPS, None ), ( EPS, 1.0 - EPS ), ( EPS, 1.0 - EPS ) )

    qm = QuickMinGarch11(guess, Garch11_NegLogLikelihood_g,
                         args=args, dt=0.1, gthr=1.e-8, verbose=verbose)

    for k, parms in enumerate(qm):
        if verbose:
            loglike = Garch11_NegLogLikelihood(parms, esq, skip)
            print(k, loglike, parms)
        if k > MAXITER:
            msg = """
            Garch11: QuickMin couldn't converge after {0;d} iterations. Last
            estimated parameters are: {1!s}""".format(k, parms)
            raise ConvergenceError(msg)

    loglike = Garch11_NegLogLikelihood(parms, esq, skip)

    covmat = np.linalg.inv(Hessian_FD_g(Garch11_NegLogLikelihood_g,
                                        parms, esq, skip))

    if np.isnan(covmat).any():
        raise ConvergenceError("Garch11, NaNs in the covariance matrix")

    return parms, -loglike, covmat


# -----------------------------------------------------------------------------
def GARCH11_grid_search(o_range, a_range, b_range, args, verbose=False):
    g_min = None 
    g_parms = None

    for o0 in o_range:
        z = np.zeros((b_range.shape[0], a_range.shape[0]))
        for j, a0 in enumerate(a_range):
            for i, b0 in enumerate(b_range):
                if a0 + b0 >= 1.0:
                    z[i,j] = 0.0
                else:
                    parms = np.array([o0, a0, b0])
                    z[i,j] = Garch11_NegLogLikelihood(parms, *args)
    
        zmin = z.min()
        bmin, amin = np.where(z == zmin)

        if verbose:
            print("minimum: {0:.2f} at {1:f},{2:f},"
                  "{3:f}".format(zmin, o0, a_range[amin], b_range[bmin]))

        g_min = min(g_min, zmin) or zmin
        g_parms = [o0, a_range[amin],
                       b_range[bmin]] if g_min == zmin else g_parms

    if verbose:
        print("global minimum is {0:.2f} at {1:f},{2:f},"
              "{3:f}".format(g_min, g_parms[0], g_parms[1], g_parms[2]))

    return g_min, np.array(g_parms)


# -----------------------------------------------------------------------------
def Garch11_CondVar(omega, alpha, beta, ret, skip):
    """
    Description:
        ...
    Inputs:
        x - ...
    Returns:
        ...
    """
    esq = (ret - ret.mean())**2
    n = len(esq)
    var = np.zeros_like(esq)
    var[0] = esq[skip:].std()

    for i in range(1, n):
        var[i] = omega + alpha*esq[i-1] + beta*var[i-1]

    return var[skip:]

# -----------------------------------------------------------------------------
def Garch11_CondVol(omega, alpha, beta, ret, skip):
    return np.sqrt(Garch11_CondVar(omega, alpha, beta, ret, skip))


# -----------------------------------------------------------------------------
def Garch11_Returns(omega, alpha, beta, vol0, ndays):
    var = vol0*vol0
    ret = np.zeros(ndays)

    for i, z in enumerate(np.random.standard_normal(ndays)):
        ret[i] = m_sqrt(var)*z
        var = omega + (alpha*z*z + beta)*var

    return ret


# -----------------------------------------------------------------------------
def Garch11_Fcast(omega, alpha, beta,
                  ret, skip, ndays, nsims=1000, covmat=None):

    if covmat is None:
        omega *= np.ones(nsims)
        alpha *= np.ones(nsims)
        beta *= np.ones(nsims)
    else:
        z = np.random.multivariate_normal((omega, alpha, beta), covmat, nsims)

        omega = z[:,0]
        alpha = z[:,1]
        beta = z[:,2]

        den = np.where(alpha + beta >= 0.999, alpha + beta + 0.001, 1.0)

        alpha /= den
        beta  /= den

    esq = (ret - ret.mean())**2
    var = esq[skip:].std()*np.zeros(nsims)
    esq = np.tile(esq, (nsims, 1))

    for i in range(1, esq.shape[1]):
        var = omega + alpha*esq[:,i-1] + beta*var

    ret = np.zeros((nsims, ndays))

    if nsims % 2 == 0:
        def randn(n):
            z = np.random.standard_normal(n / 2)
            return np.hstack((-z, z))
    else:
        def randn(n):
            return np.random.standard_normal(n)

    for i in range(ndays):
        z = randn(nsims)
        ret[:,i] = np.sqrt(var)*z
        var = omega + (alpha*z*z + beta)*var

    return np.squeeze(ret)


# ------------------------------------------------------------------------------
def Garch11_NegLogLikelihood(parms, esq, skip):
    # --- unpack parameters
    omega, alpha, beta = parms

    n = len(esq)
    var = esq[skip:].std()

    for i in range(1, skip):
        var = omega + alpha*esq[i-1] + beta*var

    loglike = -0.5*(n - skip)*m_log(2.0*m_pi)

    for i in range(skip, n):
        var = omega + alpha*esq[i-1] + beta*var
        loglike -= 0.5*(m_log(var) + esq[i] / var)

    return -loglike


# ------------------------------------------------------------------------------
def Garch11_NegLogLikelihood_g(parms, esq, skip):
    # --- unpack parameters
    omega, alpha, beta = parms

    n = len(esq)
    var = esq[skip:].std()

    for i in range(1, skip):
        var = omega + alpha*esq[i-1] + beta*var

    grad = np.zeros(3)

    g0 = 0.0
    g1 = 0.0
    g2 = 0.0

    for i in range(skip, n):
        g0 = 1.0 + beta*g0
        g1 = esq[i-1] + beta*g1
        g2 = var + beta*g2

        var = omega + alpha*esq[i-1] + beta*var
        coeff = (1.0 - esq[i] / var) / var

        grad += coeff*np.array([g0, g1, g2])

    return 0.5*grad


# ------------------------------------------------------------------------------
def IGarch11(ret, skip=10):
    """
    Description:
        ...
    Inputs:
        x - ...
    Returns:
        ...
    """
    args = ((ret - ret.mean())**2, 10)
    bounds = [0.0, 1.0]
    res = scipyopt.minimize_scalar(IGarch11_NegLogLikelihood,
                                   args=args, method="bounded", bounds=bounds)

    if not res["success"]:
         raise ConvergenceError("IGarch11: linear "
                                "optimization couldn't converge")

    return np.array([0.0, 1.0 -res["x"], res["x"]]), -res["fun"]


# ------------------------------------------------------------------------------
def IGarch11_NegLogLikelihood(beta, esq, skip):
    n = len(esq)
    var = esq[skip:].std()

    for i in range(1, skip):
        var = (1.0 - beta)*esq[i-1] + beta*var

    loglike = -0.5*(n - skip)*m_log(2.0*m_pi)

    for i in range(skip, n):
        var = (1.0 - beta)*esq[i-1] + beta*var
        loglike -= 0.5*(m_log(var) + esq[i] / var)

    return -loglike

################################################################################
#  RegTest
# ------------------------------------------------------------------------------
if __name__ == "__main__":

#    parms = [ 1.e-5, 0.10, 0.85 ]
#    ret = Garch11_Returns( *parms, vol0 = 0.01, ndays = 100, nsims = 1000 )

    parms = [ 1.e-4, 0.10, 0.85, 0.02 ]
    ret = Garch11_Returns( *parms, ndays = 1000 )

    parms, _, covmat = Garch11( ret, verbose = False )

    z = np.random.multivariate_normal( ( 0.0, 0.0, 0.0 ), covmat, 10000 )

    err_distr = lambda p, z: 1.0 / ( 1.0 + ( 1.0 - p ) / p * np.exp( z ) )

    o = err_distr( parms[0], z[:,0] )
    a = err_distr( parms[1], z[:,1] )
    b = err_distr( parms[2], z[:,2] )


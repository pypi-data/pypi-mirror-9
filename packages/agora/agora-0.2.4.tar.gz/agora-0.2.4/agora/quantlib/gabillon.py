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
"""
Core functions for multi asset Gabillon Model (G2F):

     dF(t,T)            -beta*(T-t)                      -beta*(T-t)
    -------- = sigma_S*e          *dW_S + sigma_L*( 1 - e           )*dW_L
     F(t,T)

    where: <dW_S,dW_L> = rho_SL*dt
"""
from math import exp, log, sqrt
import numpy as np

__all__ = [
    "LocalVarG2F",
    "TermVarG2F",
    "TermCovG2F",
    "TermCovG2F2Assets",
    "G2FCalibrator",
    "G2FFuturesCalibrator",
    "SwapVolG2F",
]


# -----------------------------------------------------------------------------
def MrFactor(tau, beta, T):
    """
    Description:
        Mean-reversion function B:

                         tau
                        /       - beta*( T - t )
            B(tau,T) =  | dt * e
                        /
                        0
    """
    return exp(-beta*T)*(exp(beta*tau) - 1.0) / beta


# -----------------------------------------------------------------------------
def MrFactorSq(tau, beta_k, beta_l, T_i, T_j):
    """
    Description:
        Mean-reversion function B2:

                          tau
                         /       - beta_k*( T_i - t ) - beta_l*( T_j - t )
            B2(tau,T) =  | dt * e
                         /
                         0
    """
    return (exp(-beta_k*T_i - beta_l*T_j) *
            (exp((beta_k + beta_l)*tau) - 1.0) / (beta_k + beta_l))


# -----------------------------------------------------------------------------
# Cross Correlations between diagonal terms

def rho_YL(rho_SL_kl, rho_SL_k, rho_SL_k_comp, rho_LL_kl):
    return (rho_SL_kl - rho_SL_k*rho_LL_kl) / rho_SL_k_comp


def rho_YY(rho_SL_k, rho_SL_k_comp, rho_SL_l, rho_SL_l_comp,
           rho_SS_kl, rho_LL_kl, rho_YL_kl, rho_YL_lk):
    """
    rho_SL_k, rho_SL_k_comp:  G2F parameters for asset k
    rho_SL_l, rho_SL_l_comp:  G2F parameters for asset l
    rho_SS_kl, rho_LL_kl, rho_YL_kl, rho_YL_lk:  cross terms k-l
    """
    den = rho_SL_k_comp * rho_SL_l_comp
    num = (rho_SS_kl -
           rho_SL_k*rho_SL_l*rho_LL_kl -
           rho_SL_k*rho_SL_l_comp*rho_YL_lk -
           rho_SL_l*rho_SL_k_comp*rho_YL_kl)
    return num / den


# -----------------------------------------------------------------------------
def LocalVarG2F(sig_S, sig_L, rho_SL, beta, dT):
    """
    Two factors local variance
    """
    rho_SL_cmop_sq = 1.0 - rho_SL*rho_SL

    exp1 = exp(-beta*dT)
    exp2 = exp(-2.0*beta*dT)

    return (sig_S*sig_S*rho_SL_cmop_sq*exp2 +
            (sig_S*rho_SL*exp1 + sig_L*(1.0 - exp1))**2)


# -----------------------------------------------------------------------------
def TermVarG2F(sig_S, sig_L, rho_SL, beta, tau, T):
    """
    Description:
        G2F: terminal variance for a two factors model

                               tau
                          1   /   dF(t,T)   dF(t,T)
            var(tau,T) = ---  | < ------- * ------- >
                         tau  /    F(t,T)    F(t,T)
                              0
    Inputs:
        sig_S  -  short factor volatility
        sig_L  -  long factor volatility
        rho_SL -  short-long correlation
        beta   -  mean-reversion factor
        tau    -  time to option's expiration
        T      -  time to expiration of futures contract F
    """
    B2 = MrFactorSq(tau, beta, beta, T, T)
    B = MrFactor(tau, beta, T)

    return (sig_L*sig_L*tau - 2.0*B*(sig_L*sig_L - rho_SL*sig_S*sig_L) +
            B2*(sig_S*sig_S + sig_L*sig_L - 2.0*rho_SL*sig_S*sig_L)) / tau


# -----------------------------------------------------------------------------
def TermCovG2F(sig_S, sig_L, rho_SL, beta, tau, T_i, T_j):
    """
    Description:
        G2F: terminal covariance between two futures contracts F(t,T_i) and
             F(t,T_j) on the same asset.

                               tau
                          1   /   dF(t,T_i)   dF(t,T_j)
            var(tau,T) = ---  | < --------- * --------- >
                         tau  /    F(t,T_i)    F(t,T_j)
                              0
    Inputs:
        sig_S  -  short factor volatility
        sig_L  -  long factor volatility
        rho_SL -  short-long correlation
        beta   -  mean-reversion factor
        tau    -  time to option's expiration
        T_i    -  time to expiration of futures contract F_k(T_i)
        T_j    -  time to expiration of futures contract F_l(T_j)
    """
    B2 = MrFactorSq(tau, beta, beta, T_i, T_j)
    Bij = MrFactor(tau, beta, T_i) + MrFactor(tau, beta, T_j)

    return (sig_L*sig_L*tau - Bij*(sig_L*sig_L - rho_SL*sig_S*sig_L) +
            B2*(sig_S*sig_S + sig_L*sig_L - 2.0*rho_SL*sig_S*sig_L)) / tau


# -----------------------------------------------------------------------------
def TermCovG2F2Assets(sig_S_k, sig_L_k, rho_SL_k, rho_SL_k_comp, beta_k,
                      sig_S_l, sig_L_l, rho_SL_l, rho_SL_l_comp, beta_l,
                      rho_YY_kl, rho_YL_kl, rho_YL_lk, rho_LL_kl,
                      tau, T_i, T_j):
    """
    Signature:
        TermCovG2F( sig_S_k, sig_L_k, rho_SL_k, rho_SL_k_comp, beta_k,
                    sig_S_l, sig_L_l, rho_SL_l, rho_SL_l_comp, beta_l,
                    rho_YY_kl, rho_YL_kl, rho_YL_lk, rho_LL_kl,
                    tau, T_i, T_j )
    Description:
        G2F: terminal covariance between two futures contracts F_k(t,T_i) and
             F_l(t,T_j) on different assets (k and l).

                                 tau
                            1   /   dF_k(t,T_i)   dF_l(t,T_j)
        cov(tau,T_i,T_j) = ---  | < ----------- * ----------- >
                           tau  /    F_k(t,T_i)    F_l(t,T_j)
                                0
    Inputs:
        sig_S_k   -  short factor volatility for asset k
        sig_L_k   -  long factor volatility for asset k
        rho_SL_k  -  short-long correlation for asset k
        beta_k    -  mean-reversion factor for asset k
        sig_S_l   -  short factor volatility for asset l
        sig_L_l   -  long factor volatility for asset l
        rho_SL_l  -  short-long correlation for asset l
        beta_l    -  mean-reversion factor for asset l
        rho_YY_kl -  cross-asset YY correlation (as returned by rho_YY)
        rho_YL_kl -  cross-asset YL correlation (as returned by rho_YL)
        rho_YL_lk -  cross-asset LY correlation (as returned by rho_YL)
        rho_LL_kl -  cross-asset LL correlation
        tau       -  time to option's expiration
        T_i       -  time to expiration of futures contract F_k(T_i)
        T_j       -  time to expiration of futures contract F_l(T_j)
    """
    sig_hat_SL_kl = sig_S_k*sig_L_l*rho_SL_k
    sig_hat_SL_lk = sig_S_l*sig_L_k*rho_SL_l
    sig_hat_SL_kl_comp = sig_S_k*sig_L_l*rho_SL_k_comp
    sig_hat_SL_lk_comp = sig_S_l*sig_L_k*rho_SL_l_comp

    sig_hat_LL_kl = sig_L_k*sig_L_l*rho_LL_kl

    sig_hat_kl = (sig_S_k*sig_S_l*(rho_SL_k_comp*rho_SL_l_comp*rho_YY_kl +
                                   rho_SL_k_comp*rho_YL_kl*rho_SL_l +
                                   rho_SL_l_comp*rho_YL_lk*rho_SL_k +
                                   rho_SL_k*rho_SL_l*rho_LL_kl) -
                  sig_hat_SL_kl_comp*rho_YL_kl - sig_hat_SL_lk_comp*rho_YL_lk -
                  rho_LL_kl*(sig_hat_SL_kl + sig_hat_SL_lk) + sig_hat_LL_kl)

    sig_hat_k = (sig_hat_SL_kl_comp*rho_YL_kl +
                 sig_hat_SL_kl*rho_LL_kl - sig_hat_LL_kl)
    sig_hat_l = (sig_hat_SL_lk_comp*rho_YL_lk +
                 sig_hat_SL_lk*rho_LL_kl - sig_hat_LL_kl)

    B2_klij = MrFactorSq(tau, beta_k, beta_l, T_i, T_j)
    B_ki = MrFactor(tau, beta_k, T_i)
    B_lj = MrFactor(tau, beta_l, T_j)

    return (sig_hat_kl*B2_klij +
            sig_hat_k*B_ki + sig_hat_l*B_lj + sig_hat_LL_kl*tau) / tau


# -----------------------------------------------------------------------------
class G2FCalibError(Exception):
    pass


# -----------------------------------------------------------------------------
def G2FCalibrator(sig_Black, sig_L, rho_SL, beta, tau, T):
    """
    Description:
        G2F: calibrate sig_S to term volatilities marked by traders
    Inputs:
        sig_Black -  term (Black) volatility
        sig_L     -  long factor volatility
        rho_SL    -  short-long correlation
        beta      -  mean-reversion factor
        tau       -  time to option's expiration
        T         -  time to expiration of futures contract F
    """
    B2 = MrFactorSq(tau, beta, beta, T, T)
    B = MrFactor(tau, beta, T)
    a = B2
    b = sig_L*rho_SL*(B - B2)
    c = sig_L*sig_L*(B2 - 2.0*B + tau) - sig_Black*sig_Black*tau

    delta = b*b - a*c

    if delta >= 0:
        return (-b + sqrt(delta)) / a
    else:
        raise G2FCalibError("Cannot calibrate short volatility: delta < 0")


##-----------------------------------------------------------------------------
def G2FFuturesCalibrator(sig_Black, sig_L, rho_SL, beta, tau, T):
    """
    Description:
        G2F: calibrate sig_S to term volatilities marked by traders
    Inputs:
        sig_Black -  term (Black) volatility
        sig_L     -  long factor volatility (as percentage of short vol)
        rho_SL    -  short-long correlation
        beta      -  mean-reversion factor
        tau       -  time to option's expiration
        T         -  time to expiration of futures contract F
    """
    B2 = MrFactorSq(tau, beta, beta, T, T)
    B = MrFactor(tau, beta, T)
    a = ((1.0 + sig_L*sig_L - 2.0*sig_L*rho_SL)*B2 -
         2.0*sig_L*(sig_L - rho_SL)*B + sig_L*sig_L*tau)

    return sig_Black*sqrt(tau / a)


##-----------------------------------------------------------------------------
def SwapVolG2F(PD, ED, VEDs, sig_S, sig_L, rho_SL, beta, F=None):
    """
    Description:
        This is the Black volatility for a swaption. The underlying swap is
        defined by the volatility end dates (VEDs) of the monthly contracts.
    Inputs:
        PD     - Pricing Date
        ED     - Option's expiration date
        VEDs   - Volatility End Dates (i.e. last trading day for the
                 underlying monthly contract)
        sig_S  - Sigma Short (G2F)
        sig_L  - Sigma Long (G2F)
        rho_SL - Short-Long correlation (G2F)
        beta   - Beta (G2F)
        F      - Forward curve for the underlying monthly contracts
    """
    n = len(VEDs)
    tau = (ED.ordinal - PD.ordinal) / 365.0

    # --- early return for expired swaptions
    if tau <= 0.0:
        return 0.0

    # --- if no forward prices are passed, assume they are all equal to one
    if F is None:
        F = np.ones(n)

    w = np.ones(n) / n
    T = [(ved.ordinal - PD.ordinal) / 365.0 for ved in VEDs]

    CovMat = np.zeros((n, n))

    sig_B2 = (sig_S*sig_S + sig_L*sig_L - 2.0*sig_S*sig_L*rho_SL)
    sig_B1 = (sig_L*sig_L - sig_S*sig_L*rho_SL)
    sig_Lsq = sig_L*sig_L

    for i in range(n):
        Bi = exp(-beta*T[i])*(exp(beta*tau) - 1.0) / beta
        for j in range(i, n):
            Bj = exp(-beta*T[j])*(exp(beta*tau) - 1.0) / beta
            B2 = 0.5*exp(-beta*(T[i] + T[j]))*(exp(2.0*beta*tau) - 1.0) / beta
            cov = (sig_B2*B2 - sig_B1*(Bi + Bj) + sig_Lsq*tau) / tau

            CovMat[i,j] = cov  # analysis:ignore
            CovMat[j,i] = cov  # analysis:ignore

    fw = F*w
    M1 = np.sum(fw)
    M2 = np.dot(np.dot(fw.T, np.exp(CovMat)), fw)

    return sqrt(log(M2 / (M1*M1)))

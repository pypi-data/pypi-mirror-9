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
from agora.quantlib.tree_pricers import opt_BT
from agora.quantlib.montecarlo_pricers import MC_vanilla, MC_american
from agora.econometrics.gbm_functions import GbmPricePaths

import numpy as np
import math
import unittest

# --- conversions to daily for MC paths
to_daily = 1.0 / 255.0


###############################################################################
class UnitTest(unittest.TestCase):

    def test_vanilla_convergence(self):
        # --- seed the random generator to make unittest deterministic
        np.random.seed(145)

        # --- price paths parameters
        spot, strike, vol, rd, rf, n_days = (75.0, 100.0,
                                             0.25, 0.05, 0.03, 60)

        payoff = lambda s: max(s - strike, 0.0)

        term = n_days*to_daily
        rd_daily = rd*to_daily
        rf_daily = rf*to_daily

        bs_prem = opt_BS("C", spot, strike,
                         vol, term, rd, rf, ret_type="P")

        for n_sims in (1000, 5000, 10000, 50000, 100000, 500000, 1000000):
            paths = spot*GbmPricePaths(vol*math.sqrt(to_daily), n_days,
                                       rd_daily, rf_daily, n_sims, True)

            mc_prem, mc_err = MC_vanilla(paths, payoff, rd, rf, term)

#            print(n_sims, mc_prem, mc_err, bs_prem)

    # -------------------------------------------------------------------------
    def test_american_convergence(self):
        # --- seed the random generator to make unittest deterministic
        np.random.seed(145)

        # --- price paths parameters
        spot, strike, vol, rd, rf, n_days = (75.0, 100.0,
                                             0.25, 0.05, 0.03, 60)

        payoff = lambda s: max(s - strike, 0.0)

        term = n_days*to_daily
        rd_daily = rd*to_daily
        rf_daily = rf*to_daily

        bt_prem = opt_BT("C", spot, strike, vol, term,
                         rd, rf, "AMERICAN", n_steps=4080)

        for n_sims in (1000, 5000, 10000, 50000, 100000, 250000):
            paths = spot*GbmPricePaths(vol*math.sqrt(to_daily), n_days,
                                       rd_daily, rf_daily, n_sims, False)

            mc_prem, mc_err = MC_american(paths, payoff, term, rd, rf,
                                          basis="poly", opt_type="C",
                                          spot=spot, strike=strike, vol=vol)

#            print(n_sims, mc_prem, mc_err, bt_prem)

#    # -------------------------------------------------------------------------
#    def test_vanilla(self):
#        # --- seed the random generator to make unittest deterministic
#        np.random.seed(123)
#
#        # --- price paths parameters
#        spot, vol, rd, n_sims = (100.0, 0.25, 0.05, 10000)
#
#        # --- test two scenarios for rf (i.e. smaller and larger than rd)
#        for rf in (0.03, 0.07):
#            rd_daily = rd*to_daily
#            rf_daily = rf*to_daily
#
#            for n_days in (60, 120, 255):
#                term = n_days*to_daily
#                paths = spot*GbmPricePaths(vol*math.sqrt(to_daily), n_days,
#                                           rd_daily, rf_daily, n_sims, True)
#
#                for strike in (75.0, 100, 125):
#                    # --- payoff function for a call option
#                    payoff = lambda s: max(s - strike, 0.0)
#
#                    mc_prem, mc_err = MC_vanilla(paths, payoff, rd, rf, term)
#
#                    bs_prem = opt_BS("C", spot, strike,
#                                     vol, term, rd, rf, ret_type="P")
#
#                    delta = abs(mc_prem - bs_prem)
#
#                    # --- chack that estimated MC premium is compatible with
#                    #     the BS one within 2 sigma (not very stringent).
#                    self.assertLessEqual(delta / mc_err, 2.0)

    # -------------------------------------------------------------------------
#    def test_american(self):
#        # --- seed the random generator to make unittest deterministic
#        np.random.seed(145)
#
#        # --- price paths parameters
#        spot, vol, rd, n_sims = (100.0, 0.25, 0.05, 5000)
#
#        # --- conversions to daily for MC paths
#        to_daily = 1.0 / 255.0
#
#        # --- test two scenarios for rf (i.e. smaller and larger than rd)
#        for rf in (0.03, 0.07):
#            rd_daily = rd*to_daily
#            rf_daily = rf*to_daily
#
#            for n_days in (60, 120, 255):
#                term = n_days*to_daily
#                paths = spot*GbmPricePaths(vol*math.sqrt(to_daily), n_days,
#                                           rd_daily, rf_daily, n_sims, False)
#
#                for strike in (75.0, 100, 125):
#                    # --- payoff function for a call option
#                    payoff = lambda s: max(s - strike, 0.0)
#
#                    mc_prem, mc_err = MC_american(paths, payoff, term, rd, rf,
#                                                  basis="poly", opt_type="C",
#                                                  spot=spot, strike=strike, vol=vol)
#
#                    bt_prem = opt_BT("C", spot, strike, vol, term,
#                                     rd, rf, "AMERICAN", n_steps=4080)
#
#                    delta = abs(mc_prem - bt_prem)
#
#                    # --- chack that estimated MC premium is compatible with
#                    #     the BS one within 2 sigma (not very stringent).
#                    self.assertLessEqual(delta / mc_err, 2.0)


if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

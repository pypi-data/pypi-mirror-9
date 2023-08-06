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

from agora.quantlib.black_scholes import opt_BS, opt_BAW, opt_JZ, implied_vol
from agora.quantlib.tree_pricers import opt_BT

import unittest

# --- reference table of black-scholes results (from gnumeric)
BLACK_SCHOLES_REF = {
    # --- short dated, negative carry
    ("C", 40.0, 50.0, 0.20, 0.25, 0.025, 0.050): (0.016496, 0.012264),
    ("P", 40.0, 50.0, 0.20, 0.25, 0.025, 0.050): (10.201858, -0.975314),
    ("C", 50.0, 50.0, 0.20, 0.25, 0.025, 0.050): (1.824346,  0.488864),
    ("P", 50.0, 50.0, 0.20, 0.25, 0.025, 0.050): (2.133931, -0.498714),
    ("C", 60.0, 50.0, 0.20, 0.25, 0.025, 0.050): (9.651571, 0.952921),
    ("P", 60.0, 50.0, 0.20, 0.25, 0.025, 0.050): (0.085377, -0.034657),
    # --- long dated, positive carry
    ("C", 40.0, 50.0, 0.20, 1.00, 0.005, 0.010): (0.559848, 0.147521),
    ("P", 40.0, 50.0, 0.20, 1.00, 0.005, 0.010): (10.708478, -0.842529),
    ("C", 50.0, 50.0, 0.20, 1.00, 0.005, 0.010): (3.830202, 0.524620),
    ("P", 50.0, 50.0, 0.20, 1.00, 0.005, 0.010): (4.078334, -0.465430),
    ("C", 60.0, 50.0, 0.20, 1.00, 0.005, 0.010): (10.767967, 0.829743),
    ("P", 60.0, 50.0, 0.20, 1.00, 0.005, 0.010): (1.115601, -0.160306),
}


###############################################################################
class UnitTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_opt_BS(self):
        for parms, (premium, delta) in BLACK_SCHOLES_REF.items():
            p = opt_BS(*parms, ret_type="Premium")
            d = opt_BS(*parms, ret_type="Delta")
            self.assertAlmostEqual(p, premium, 6)
            self.assertAlmostEqual(d, delta, 6)

    # -------------------------------------------------------------------------
    def test_american_pricers(self):
        spot, vol, rd = 100.0, 0.25, 0.05

        # --- test two scenarios for rf (i.e. smaller and larger than rd)
        for rf in (0.03, 0.07):
            for n_days in (60, 120, 255, 510):
                term = n_days / 255.0
                for strike in (75.0, 100, 125):
                    # --- binomial tree: used as benchmark
                    bt_c = opt_BT("C", spot, strike,
                                  vol, term, rd, rf, "A", n_steps=1020)
                    bt_p = opt_BT("P", spot, strike,
                                  vol, term, rd, rf, "A", n_steps=1020)

                    baw_c = opt_BAW("C", spot, strike, vol, term, rd, rf)
                    baw_p = opt_BAW("P", spot, strike, vol, term, rd, rf)

                    c_err = abs(bt_c / baw_c - 1.0)
                    p_err = abs(bt_p / baw_p - 1.0)

                    # --- BAW: test for 4% convergence level (2% can be
                    #          achieved increasing n_steps to 4080)
                    self.assertLessEqual(c_err, 0.04)
                    self.assertLessEqual(p_err, 0.04)

                    jz_c = opt_JZ("C", spot, strike, vol, term, rd, rf)
                    jz_p = opt_JZ("P", spot, strike, vol, term, rd, rf)

                    c_err = abs(bt_c / jz_c - 1.0)
                    p_err = abs(bt_p / jz_p - 1.0)

                    # --- J-Z: test for 1% convergence level
                    self.assertLessEqual(c_err, 0.01)
                    self.assertLessEqual(p_err, 0.01)

    # -------------------------------------------------------------------------
    def test_implied_vols(self):
        strike = 100.0
        rd = 0.05
        for vol in (0.12, 0.30, 0.50):
            for term in (0.25, 0.50, 0.75):
                for rf in (0.00, 0.05, 0.10):
                    for spot in (95.0, 100.0, 105.0):
                        eu_P = opt_BS("P",  spot, strike, vol, term, rd, rf)
                        am_P = opt_BAW("P",  spot, strike, vol, term, rd, rf)
                        eu_C = opt_BS("C", spot, strike, vol, term, rd, rf)
                        am_C = opt_BAW("C", spot, strike, vol, term, rd, rf)

                        iv_eu_P = implied_vol("P", eu_P, spot, strike,
                                              term, rd, rf, american=False)
                        iv_am_P = implied_vol("P", am_P, spot, strike,
                                              term, rd, rf, american=True)
                        iv_eu_C = implied_vol("C", eu_C, spot, strike,
                                              term, rd, rf, american=False)
                        iv_am_C = implied_vol("C", am_C, spot, strike,
                                              term, rd, rf, american=True)

                        self.assertAlmostEqual(iv_eu_P, vol, 3)
                        self.assertAlmostEqual(iv_am_P, vol, 3)
                        self.assertAlmostEqual(iv_eu_C, vol, 3)
                        self.assertAlmostEqual(iv_am_C, vol, 3)


if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

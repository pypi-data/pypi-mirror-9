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

from agora.econometrics.gbm_functions import GbmPricePaths

import numpy as np
import math
import unittest

to_daily = 1.0 / 255.0


###############################################################################
class UnitTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_mean(self):
        # --- seed the random generator to make unittest deterministic
        np.random.seed(145)

        n_days, vol, rd, rf, n_sims = (255, 0.25, 0.05, 0.03, 10000)
        rd_daily = rd*to_daily
        rf_daily = rf*to_daily

        paths = GbmPricePaths(vol*math.sqrt(to_daily), n_days,
                              rd_daily, rf_daily, n_sims, False)

        exact_mean = np.exp((rd - rf)*np.cumsum(np.ones(n_days))*to_daily)
        error = np.abs(paths[1:,:].mean(axis=1) / exact_mean - 1.0)

        # --- convergence within 1%
        self.assertFalse(np.any(error > 0.01))

    # -------------------------------------------------------------------------
    def test_std(self):
        # --- seed the random generator to make unittest deterministic
        np.random.seed(145)

        n_days, vol, rd, rf, n_sims = (255, 0.25, 0.05, 0.03, 100000)
        rd_daily = rd*to_daily
        rf_daily = rf*to_daily

        paths = GbmPricePaths(vol*math.sqrt(to_daily), n_days,
                              rd_daily, rf_daily, n_sims, False)

        exact_std = vol*np.sqrt(np.cumsum(np.ones(n_days))*to_daily)
        error = np.abs(np.log(paths[1:,:]).std(axis=1) / exact_std - 1.0)

        # --- convergence within 1%
        self.assertFalse(np.any(error > 0.01))

if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

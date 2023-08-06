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

from agora.quantlib.tree_pricers import opt_BT
from agora.quantlib.test.test_black_scholes import BLACK_SCHOLES_REF

import unittest


###############################################################################
class UnitTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    def test_opt_BS(self):
        for parms, (premium, delta) in BLACK_SCHOLES_REF.items():
            # --- NB: convergence to the exact value is very slow...
            self.assertAlmostEqual(opt_BT(*parms, n_steps=510), premium, 2)
            self.assertAlmostEqual(opt_BT(*parms, n_steps=4080), premium, 3)


if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

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

from onyx.core import GetVal

import agora.tradables.ufo_fx_forward as ufo_fx_forward
import unittest


###############################################################################
class UnitTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.securities = ufo_fx_forward.prepare_for_test()

    def setUp(self):
        self.fwdeur = self.securities[0]
        self.fwdgbp = self.securities[1]

    def test_MktVal(self):
        self.assertAlmostEqual(GetVal(self.fwdeur, "MktVal"), -0.15 / 1.15, 8)
        self.assertAlmostEqual(GetVal(self.fwdgbp, "MktVal"), -0.50 / 1.50, 8)

    def test_MktValUSD(self):
        self.assertAlmostEqual(GetVal(self.fwdeur, "MktValUSD"), -0.15, 8)
        self.assertAlmostEqual(GetVal(self.fwdgbp, "MktValUSD"), -0.50, 8)

if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

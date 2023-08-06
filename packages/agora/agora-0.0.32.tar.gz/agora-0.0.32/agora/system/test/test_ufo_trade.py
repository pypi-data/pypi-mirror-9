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

from onyx.core import GetVal, Structure

import agora.system.ufo_trade as ufo_trade
import unittest


###############################################################################
class UnitTest(unittest.TestCase):
    ##-------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.trades = ufo_trade.prepare_for_test()

    def setUp(self):
        self.cash_trade = self.trades[0]
        self.cfd_trade = self.trades[1]

    def test_MktValUSD(self):
        self.assertAlmostEqual(GetVal(self.cash_trade, "MktValUSD"), 150.0, 8)
        self.assertAlmostEqual(GetVal(self.cfd_trade, "MktValUSD"), 150.0, 8)

    def test_Deltas(self):
        ref = Structure([("EQ NG/ LN", -1000.0)])
        self.assertEqual(GetVal(self.cash_trade, "Deltas"), ref)
        self.assertEqual(GetVal(self.cfd_trade, "Deltas"), ref)

    def test_Exposures(self):
        # --- cash trade is denominated in GBP
        self.assertEqual(GetVal(self.cash_trade, "GrossExposure"), 9000.0)
        self.assertEqual(GetVal(self.cash_trade, "NetExposure"), -9000.0)
        # --- cfd trade is denominated in USD (PaymentUnit is not set)
        self.assertEqual(GetVal(self.cfd_trade, "GrossExposure"), 13500.0)
        self.assertEqual(GetVal(self.cfd_trade, "NetExposure"), -13500.0)

if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

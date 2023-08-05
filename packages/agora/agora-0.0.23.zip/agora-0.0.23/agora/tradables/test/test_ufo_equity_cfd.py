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

from onyx.core import GetVal, ChildrenIterator

import agora.tradables.ufo_equity_cfd as ufo_equity_cfd
import unittest


###############################################################################
class UnitTest(unittest.TestCase):
    ##-------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.securities = ufo_equity_cfd.prepare_for_test()

    def setUp(self):
        self.sec = self.securities[0]

    def test_MktVal(self):
        self.assertAlmostEqual(GetVal(self.sec, "MktVal"), -0.1, 8)

    def test_MktValUSD(self):
        self.assertAlmostEqual(GetVal(self.sec, "MktValUSD"), -0.15, 8)

    def test_TradeTypes(self):
        tt = {
            "Buy": "BuySecurities",
            "Sell": "SellSecurities",
            "ExDividend": "ExDividendSecurities",
        }
        self.assertEqual(GetVal(self.sec, "TradeTypes"), tt)

    def test_Children(self):
        kids = sorted(set(ChildrenIterator(self.sec, "MktValUSD", "Spot")))
        self.assertEqual(kids, ["EQ NG/ LN", "GBP/USD"])

if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

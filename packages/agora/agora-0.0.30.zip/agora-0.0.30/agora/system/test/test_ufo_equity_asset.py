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

import agora.system.ufo_equity_asset as ufo_equity_asset
import unittest


###############################################################################
class UnitTest(unittest.TestCase):
    ##-------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        ufo_equity_asset.prepare_for_test()

    def test_Ticker(self):
        self.assertEqual(GetVal("EQ IBM US", "Ticker"), "IBM")
        self.assertEqual(GetVal("EQ NG/ LN", "Ticker"), "NG/")
        self.assertEqual(GetVal("EQ NG/ LN", "Ticker", "Google"), "NG")
        self.assertEqual(GetVal("EQ NG/ LN", "Ticker", "Yahoo"), "NG")
        self.assertEqual(GetVal("EQ NG/ LN", "Ticker", "WSJ"), "NG.")

    def test_Spot(self):
        self.assertEqual(GetVal("EQ IBM US", "Spot"), 100.0)
        self.assertEqual(GetVal("EQ NG/ LN", "Spot"), 9.0)


if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

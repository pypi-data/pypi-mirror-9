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

import agora.risk.ufo_risk as ufo_risk
import unittest


###############################################################################
class UnitTest(unittest.TestCase):
    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        cls.books = ufo_risk.prepare_for_test()

    def setUp(self):
        self.book = self.books[0]

    def compareStructures(self, first, second, places):
        self.assertEqual(first.keys(), second.keys())
        for key, value in first.items():
            self.assertAlmostEqual(value, second[key], places)

    def test_MktVal(self):
        self.assertAlmostEqual(GetVal(self.book, "MktVal"), 200.0, 8)

    def test_MktValUSD(self):
        self.assertAlmostEqual(GetVal(self.book, "MktValUSD"), 300.0, 8)

    def test_Deltas(self):
        ref_deltas = Structure([("EQ NG/ LN", -2000.0)])
        self.compareStructures(GetVal(self.book, "Deltas"), ref_deltas, 4)

    def test_Exposures(self):
        self.assertAlmostEqual(GetVal(self.book, "GrossExposure"), 18000.0, 4)
        self.assertAlmostEqual(GetVal(self.book, "NetExposure"), -18000.0, 4)

    def test_FX(self):
        ref_fx = Structure([
            ("EUR/USD", 7913.043478260922),
            ("GBP/USD", -6067.273394006065)
        ])
        self.assertAlmostEqual(GetVal(self.book, "FxExposures"), ref_fx, 8)

if __name__ == "__main__":
    from agora.corelibs.unittest_utils import AgoraTestRunner
    unittest.main(testRunner=AgoraTestRunner)

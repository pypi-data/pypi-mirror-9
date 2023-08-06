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

import datetime
import time

__all__ = ["StaticReq", "RealTimeReq"]

REFRESH = 120  # refresh interval in seconds


###############################################################################
class StaticReq(object):
    # -------------------------------------------------------------------------
    def __init__(self, args):
        self.args = args
        self.date = datetime.date.today()

    # -------------------------------------------------------------------------
    def __hash__(self):
        return hash((self.args, self.date))

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.args == other.args and self.date == other.date)

    # -------------------------------------------------------------------------
    def is_valid(self):
        return self.date == datetime.date.today()


###############################################################################
class RealTimeReq(object):
    # -------------------------------------------------------------------------
    def __init__(self, args):
        self.args = args
        self.time = 0

    # -------------------------------------------------------------------------
    def __hash__(self):
        return hash(self.args)

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.args == other.args

    # -------------------------------------------------------------------------
    def is_valid(self):
        return time.time() <= self.time + REFRESH

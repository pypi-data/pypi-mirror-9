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

from onyx.core import AddObj, ExistsInDatabase, CreateInMemory
from agora.corelibs.onyx_utils import OnyxInit

import onyx
import unittest
import os

__all__ = ["AddIfMissing", "AgoraTestRunner"]


##-----------------------------------------------------------------------------
def AddIfMissing(obj, in_memory=False):
    if not ExistsInDatabase(obj.Name):
        if in_memory:
            return CreateInMemory(obj)
        else:
            return AddObj(obj)
    return obj


###############################################################################
class AgoraTestClient(onyx.database.objdb.ObjDbDummyClient):
    ##-------------------------------------------------------------------------
    def get(self, name, refresh=False):
        return super().get(name)


###############################################################################
class AgoraTestRunner(unittest.TextTestRunner):
    ##-------------------------------------------------------------------------
    def run(self, test):
        objdb = AgoraTestClient(database="test", user="testuser")
        tsdb = os.getenv("TSDB_TEST", default="TsDb")
        with OnyxInit(objdb=objdb, tsdb=tsdb):
            return super().run(test)

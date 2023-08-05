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

import onyx.core
import contextlib
import os

__all__ = ["OnyxInit", "OnyxStartup"]


##-----------------------------------------------------------------------------
def OnyxInit(objdb=None, tsdb=None):
    """
    Description:
        Activate onyx databases and graph using the respective context
        managers.
    Inputs:
        objdb - an instance of an ObjDb client or the name of a valid ObjDb
        tsdb  - the name of a valid TsDb
    Returns:
        A stack of context managers.
    """
    objdb = objdb or os.getenv("OBJDB_PROD", default="ProdDb")
    tsdb = tsdb or os.getenv("TSDB_PROD", default="TsDb")

    stack = contextlib.ExitStack()
    stack.enter_context(onyx.core.UseDatabase(objdb))
    stack.enter_context(onyx.core.TsDbUseDatabase(tsdb))
    stack.enter_context(onyx.core.UseGraph())

    return stack


##-----------------------------------------------------------------------------
def OnyxStartup(objdb=None, tsdb=None):
    stack = OnyxInit(objdb, tsdb)
    stack.__enter__()
    print("""Onyx has been fired up... Good luck!!!""")
    return {key: value
            for key, value in onyx.core.__dict__.items()
            if not key.startswith("__")}

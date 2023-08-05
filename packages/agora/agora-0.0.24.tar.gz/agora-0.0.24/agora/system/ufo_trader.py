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

from onyx.core import UfoBase, StringField, BoolField

__all__ = ["Trader"]


###############################################################################
class Trader(UfoBase):
    """
    Abacus class used to represent a system user (generally a trader).
    """
    Group = StringField()
    Superuser = BoolField(default=False)


##-----------------------------------------------------------------------------
def prepare_for_test():
    from agora.corelibs.unittest_utils import AddIfMissing
    traders = [
        AddIfMissing(Trader(Name="TEST_TRADER1", Group="TEST_GROUP")),
        AddIfMissing(Trader(Name="TEST_TRADER2", Group="TEST_GROUP")),
    ]
    return [trader.Name for trader in traders]

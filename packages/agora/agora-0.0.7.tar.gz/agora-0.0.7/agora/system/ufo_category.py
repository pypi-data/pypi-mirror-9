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

from onyx.core import UfoBase, SetField, DictField

__all__ = ["Category"]

###############################################################################
class Category(UfoBase):
    """
    Class used to collect related symbol names.
    """
    Symbols = SetField()
    Filters = DictField()

    ##-------------------------------------------------------------------------
    ##  implement a few methods to act on the internal set of symbols

    def add(self, item):
        self.Symbols.add(item)

    def remove(self, item):
        self.Symbols.remove(item)

    def pop(self, item):
        self.Symbols.pop(item)

    def __contains__(self, item):
        return item in self.Symbols

    def __iter__(self):
        return self.Symbols.__iter__()

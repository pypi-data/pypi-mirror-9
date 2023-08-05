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

from onyx.database.objdb_api import AddDatedObj, GetDatedObj, UpdateDatedObj
from onyx.core import (UfoBase, BoolField, DictField, ObjDbQuery, ObjNotFound,
                       GraphNodeVt, GetVal)

__all__ = ["Archivable"]


###############################################################################
class Archivable(UfoBase):
    """
    Base class for all archivable UFO objects.
    """
    # --- private flag used to identify head/dated objects
    _p_is_dated = BoolField(default=False)
    # --- attributes that are retrieved using market indirection are stored
    #     here (this is left empty for the head object)
    _p_vt_data = DictField(default=dict())

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def DateOfDatedObj(self, graph):
        obj = GetDatedObj(graph(self, "Name"),
                          graph("Database", "MktDataDate"),
                          graph("Database", "ForceStrict"))
        return obj.LastUpdated

    ##-------------------------------------------------------------------------
    def add_dated(self, vtname, date, value):
        if self._p_is_dated:
            raise NotImplementedError()
        else:
            try:
                dated_obj = GetDatedObj(self.Name, date, strict=True)
                dated_obj._p_vt_data[vtname] = value
                overwritable = GetVal("Database", "ArchivedOverwritable")
                UpdateDatedObj(dated_obj, date, overwrite=overwritable)
            except ObjNotFound:
                dated_obj = self.clone(name=self.Name)
                dated_obj._p_is_dated = True
                dated_obj._p_vt_data[vtname] = value
                AddDatedObj(dated_obj, date)

    ##-------------------------------------------------------------------------
    @property
    def is_head(self):
        return not self._p_is_dated

    ##-------------------------------------------------------------------------
    def delete(self):
        """
        Invoked when the head object is deleted from database.
        """
        if self.is_head:
            ObjDbQuery("DELETE FROM Archive "
                       "WHERE Name = %s", parms=(self.Name,))

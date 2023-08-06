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
from onyx.core import (Date, Curve, Knot,
                       UfoBase, BoolField, DictField, ObjDbQuery, ObjNotFound,
                       GraphNodeVt, GetVal)

__all__ = ["Archivable"]

GET_HISTORY_QUERY = """
SELECT Date, Data->'_p_vt_data'->'{0:s}' as {0:s}
FROM Archive
WHERE Name=%s AND Date BETWEEN COALESCE(%s,%s) AND COALESCE(%s,%s)
ORDER BY Date;"""

GET_MOST_RECENT = """
SELECT MAX(Date) FROM Archive
WHERE Name=%s AND Date <= COALESCE(%s,%s)
"""


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

    # -------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def DateOfDatedObj(self, graph):
        """
        Description:
            Return the date of the current dated object (according to
            Database->MktDataDate and Database->ForceStrict).
        Inputs:
            None
        Returns:
            A Date.
        """
        obj = GetDatedObj(graph(self, "Name"),
                          graph("Database", "MktDataDate"),
                          graph("Database", "ForceStrict"))
        return obj.Date

    # -------------------------------------------------------------------------
    @GraphNodeVt()
    def LastBefore(self, graph, date=None):
        """
        Description:
            Return the date of the most recent dated object.
        Inputs:
            date - look for dated objects with Date earlier than this value.
        Returns:
            A Date.
        """
        parms = (graph(self, "Name"), date, Date.high_date())
        res = ObjDbQuery(GET_MOST_RECENT, parms, attr="fetchone")
        if res.max is None:
            raise ObjNotFound("{0:s} not found for any date earlier"
                              "than {1:s}".format(graph(self, "Name"), date))
        else:
            return res.max

    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    @property
    def is_head(self):
        return not self._p_is_dated

    # -------------------------------------------------------------------------
    def delete(self):
        """
        Invoked when the head object is deleted from database.
        """
        if self.is_head:
            ObjDbQuery("DELETE FROM Archive "
                       "WHERE Name = %s", parms=(self.Name,))

    # -------------------------------------------------------------------------
    def get_history(self, vt_name, start, end):
        query = GET_HISTORY_QUERY.format(vt_name)
        parms = (self.Name, start, Date.low_date(), end, Date.high_date())
        crv = Curve.__new__(Curve)
        crv.knot_cls = Knot
        crv.data = [Knot(Date.parse(r[0]), r[1])
                    for r in ObjDbQuery(query, parms, attr="fetchall")]
        return crv

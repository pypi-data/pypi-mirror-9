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
"""
This module defines the basic API and abstract base classes for all tradable
objects (securities).
"""

from onyx.core import (Structure, UfoBase, GetObj, AddObj, ObjNotFound,
                       CreateInMemory, GraphNodeVt)

import abc
import re
import hashlib
import math

__all__ = [
    "TradableError",
    "NamedByInference",
    "TradableObj",
    "AgingTradableObj",
    "HashInstreams",
    "InferredName",
    "AddByInference",
]


###############################################################################
class TradableError(Exception):
    pass


###############################################################################
class NamedByInference(UfoBase):
    """
    Abstract base class for all objects that require automatic naming. These
    are generally children of tradables but never tradables themselves.
    """
    ##-------------------------------------------------------------------------
    def __post_init__(self):
        self.Name = None

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def ImpliedName(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def Leaves(self, graph):
        return Structure({self.Name: 1.0})


###############################################################################
class TradableObj(NamedByInference):
    """
    Abstract base class for all tradable objects (securities). This provides
    the basic interface that each tradable needs to expose.
    """
    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def MktVal(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def MktValUSD(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def TradeTypes(self, graph):
        return {
            "Buy": "BuySecurities",
            "Sell": "SellSecurities",
        }

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def BuySecurities(self, graph):
        return [{"Security": self, "Quantity": 1.0}]

    ##-------------------------------------------------------------------------
    @GraphNodeVt("Property")
    def SellSecurities(self, graph):
        return [{"Security": self, "Quantity": -1.0}]

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def ExpectedSecurities(self, graph, key):
        """
        Return a list of securities and quantities as follows:
        [
            {"Security": sec_1, "Quantity": qty_1},
            {"Security": sec_2, "Quantity": qty_2},
            ...
        ]
        """
        return graph(self, graph(self, "TradeTypes")[key])


###############################################################################
class AgingTradableObj(TradableObj):
    """
    Abstract base class for all tradable objects (securities) that require an
    aging mechanism.

    The aging mechanism must be implemented as follows:
        - ExpectedSecurities returns a list dictionaries with expected
          security and expected quantity:
              [{"Security": sec, "Quantity": qty}, ...]
          The list is generated based on the value of ExpectedTransaction and
          the TradeTypes mapping.
        - ExpectedTransaction returns a string with the transaction expected to
          take place at the NextTransactionDate (such as Exercise, Expire,
          Pay, etc). Such string must be defined in TradeTypes.
        - NextTransactionDate returns the future date when a new event takes
          place.
    """
    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def NextTransactionDate(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @abc.abstractmethod
    def ExpectedTransaction(self):
        raise NotImplementedError()

    ##-------------------------------------------------------------------------
    @GraphNodeVt()
    def ExpectedSecurities(self, graph, key=None):
        if key is None:
            key = graph(self, "ExpectedTransaction")
        return graph(self, graph(self, "TradeTypes")[key])


##-----------------------------------------------------------------------------
def HashInstreams(obj, nchars, skip=None):
    """
    Description:
        ...
    Inputs:
        obj    - instance of a class derived from UfoBase
        nchars - number of characters in the hash
        skip   - a set of Instreams to skip
    Returns:
        A string.
    """
    skip = skip or {}
    children = set(obj._json_fields).difference(skip)

    mush = ["{0!r}".format(getattr(obj, attr)) for attr in children]
    mush = "".join(mush).encode("utf-8")
    mush = hashlib.sha224(mush).hexdigest()

    n = int(math.ceil(len(mush) / float(nchars)))

    return mush[::n].upper()


##-----------------------------------------------------------------------------
def InferredName(obj):
    """
    Description:
        ...
    Inputs:
        obj - instance of a class derived from UfoBase
    Returns:
        A string.
    """
    if not isinstance(obj, NamedByInference):
        raise TradableError("InferredName error for {0:s}.\nOnly"
                            "objects derived from NamedByInference "
                            "can have an InferredName".format(type(obj)))

    imp_name = obj.ImpliedName

    # --- check if implied name supports collision bit
    match = re.search("{0:[1-9]d}", imp_name)
    if match:
        for k in range(10**int(match.group()[3:-2])):
            name = imp_name.format(k)
            # --- here we check if an object with this name already exists in
            #     database and if such object is the same as obj
            try:
                if obj == GetObj(name):
                    return name
                else:
                    continue
            except ObjNotFound:
                return name
    else:
        try:
            if obj == GetObj(imp_name):
                return imp_name
        except ObjNotFound:
            return imp_name

    # --- nothing worked, raise an exception
    raise TradableError("ImpliedName collision problem for "
                        "<{0:s} - {1:s}>".format(obj.Name, obj.ObjType))


##-----------------------------------------------------------------------------
def AddByInference(obj, in_memory=False):
    """
    Description:
        ...
    Inputs:
        obj       - instance of a class derived from UfoBase
        in_memory - if True, create object in memory
    Returns:
        The object's instance.
    """
    obj.Name = InferredName(obj)

    if in_memory:
        return CreateInMemory(obj)
    else:
        try:
            return GetObj(obj.Name, refresh=True)
        except ObjNotFound:
            return AddObj(obj)

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

from onyx.core import GraphNodeVt, GetDatedObj

import types

__all__ = ["RetainedFactory", "MktIndirectionFactory", "InheritAsProperty"]


###############################################################################
class RetainedFactory(object):
    """
    ValueType factory that implements a descriptor protocol used to represent
    pseudo-attribute VTs, i.e. VTs that can be set but are not persisted in
    database.
    Typical use is in the implementation of edit screens and the typical
    syntax is as follows:

        @RetainedFactory(default=...)
        def MyVt(self, graph): pass
    """
    # -------------------------------------------------------------------------
    def __init__(self, default):
        self.value = default

    # -------------------------------------------------------------------------
    def __call__(self, func):
        def getter(instance, graph):
            return self.value

        def setter(instance, graph, value):
            self.value = value

        # --- return a settable descriptor ValueType
        return GraphNodeVt("Settable", getter, setter)(func)


# -----------------------------------------------------------------------------
class MktIndirectionFactory(object):
    """
    ValueType factory that implements a descriptor protocol used for market
    data indirection.

    THIS DECORATOR CAN ONLY BE APPLIED TO METHODS OF A SUBCLASS OF Archivable.

    Typical use is as follows:

        @MktIndirectionFactory(FloatField)
        def MarketizedVt(self, graph): pass

    MarketizedVt is created as a Property ValueType that fetches archived data
    by accessing the corresponding dated object. Consistency with the field
    type is enforced.

    NB: the dated object is fetched referencing the MktDataDate VT of the
        Database object.
    """
    # -------------------------------------------------------------------------
    def __init__(self, field_type):
        self.field = field_type()

    # -------------------------------------------------------------------------
    def __call__(self, func):
        vtname = func.__name__

        # --- descriptor protocol: getter
        def getter(instance, graph):
            if instance._p_is_dated:
                # --- this is the dated object: return VT data
                return self.field.from_json(instance._p_vt_data[vtname])
            else:
                # --- this is the "head" object: get VT data from dated object
                dated_obj = GetDatedObj(graph(instance, "Name"),
                                        graph("Database", "MktDataDate"),
                                        graph("Database", "ForceStrict"))
                return self.field.from_json(dated_obj._p_vt_data[vtname])

        getter.__name__ = vtname

        # --- create a property descriptor ValueType and add field_type to it
        descriptor = GraphNodeVt("Property")(getter)
        descriptor.field = self.field

        return descriptor


# -----------------------------------------------------------------------------
class InheritAsProperty(object):
    """
    Description:
        Class decorator
    Inputs:
        attrs      - a list of stored attributes of the super-class that are
                     to be replaced by Property value types.
        value_type - a pointer to the instance of the ufo class from which we
                     are inheriting stored attributes as properties
    Returns:
        Decorator function
    """
    template = ("def template(self, graph):\n"
                "    return graph(graph(self, '{0:s}'), '{1:s}')")

    # -------------------------------------------------------------------------
    def __init__(self, attrs, value_type):
        self.attrs = attrs
        self.value_type = value_type

    # -------------------------------------------------------------------------
    def __call__(self, cls):
        for attr in self.attrs:
            # --- discard from set of StoredAttrs attributes (discard does
            #     nothing if cls doesn't have such attribute)
            cls._json_fields.discard(attr)
            cls.StoredAttrs.discard(attr)

            # --- create Property-ValueType
            mod = types.ModuleType("__templates")
            exec(self.template.format(self.value_type, attr), mod.__dict__)
            func = types.FunctionType(mod.template.__code__, {}, name=attr)
            setattr(cls, attr, GraphNodeVt("Property")(func))

        return cls

###############################################################################
#
#   Onyx Portfolio & Risk Management Framework
#
#   Copyright 2014 Carlo Sbraccia
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
This module implements a Dependency Graph that works on top of the ObjDb
object database
"""

import onyx.database as onyx_db
import onyx.depgraph as onyx_dg

import weakref
import copy

__all__ = ["GraphError", "GraphNodeError"]


###############################################################################
class GraphError(Exception):
    pass


###############################################################################
class GraphNodeError(Exception):
    pass


###############################################################################
class DependencyGraph(dict):
    """
    Class representing the onyx Dependency Graph (a Directed Acyclic Graph).
    Current implementation uses a dictionary that maps (ObjectName, VT) tuples
    to graph nodes (instances of GraphNode class).
    """
    ##-------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        # --- hard references to the retrived objects are kept here so that
        #     any weak-references pointing to them won't disappear if and when
        #     the instance retrived from database is garbage collected
        self.objects = dict()
        # --- for each object, we keep the set of VTs that have been visited
        #     while building the graph
        self.vts_by_obj = dict()

    ##-------------------------------------------------------------------------
    def clear(self):
        super().clear()
        self.objects.clear()
        self.vts_by_obj.clear()


##-----------------------------------------------------------------------------
def CreateNode(node_def):
    """
    Description:
        Helper function used to create a new node.
    Inputs:
        node_def - the (ObjectName, VT) tuple
    Returns:
        A subclass of GraphNode.
    """
    obj_name, VT = node_def

    # --- the instance of the graph keeps trak of references to objects that
    #     have nodes in the current graph and maps VTs by object
    try:
        onyx_dg.graph.vts_by_obj[obj_name].add(VT)
    except KeyError:
        onyx_dg.graph.vts_by_obj[obj_name] = {VT}

    try:
        obj = onyx_dg.graph.objects[obj_name]
    except KeyError:
        obj = onyx_db.obj_clt.get(obj_name)
        onyx_dg.graph.objects[obj_name] = obj

    # --- all Instreams are settable by definition
    if VT in obj.Instreams:
        return GraphNodeSettable(VT, weakref.ref(obj))

    # --- look-up the VT definition in the __dict__ of the class object
    try:
        VT_descriptor = obj.__class__.__dict__[VT]
    except KeyError:
        raise AttributeError("'{0:s}' object has no "
                             "attribute '{1:s}'".format(obj.ObjType, VT))

    if hasattr(VT_descriptor, "fset"):
        return GraphNodeSettable(VT, weakref.ref(obj))
    elif callable(VT_descriptor):
        return GraphNodeCalc(VT, weakref.ref(obj))
    else:
        return GraphNode(VT, weakref.ref(obj))


###############################################################################
class GraphNode(object):
    """
    Base class representing a node in the Dependency Graph. Implements methods
    to get the node value (using memoization), to invalidate it (when
    recalculation is needed), and to clone the node (for diddling).
    This is used by ValueTypes implementing the property descriptor.
    """
    __slots__ = ("VT", "obj_ref", "parents",
                 "children", "valid", "value", "old_node")

    ##-------------------------------------------------------------------------
    def __init__(self, VT, obj_ref):
        self.VT = VT
        self.obj_ref = obj_ref
        self.parents = set()
        self.children = set()
        self.valid = False
        self.value = None
        self.old_node = None

    ##-------------------------------------------------------------------------
    def get_value(self):
        if self.valid:
            return self.value
        else:
            self.value = getattr(self.obj_ref(), self.VT)
            self.valid = True
            return self.value

    ##-------------------------------------------------------------------------
    def clone(self):
        cls = self.__class__
        new_node = cls.__new__(cls)
        for attr in self.__slots__:
            setattr(new_node, attr, copy.deepcopy(getattr(self, attr)))
        return new_node

    ##-------------------------------------------------------------------------
    def invalidate(self):
        if self.valid:
            # --- invalidate this node
            self.valid = False
            # --- recursively invalidate all parents
            for parent in self.parents:
                onyx_dg.graph[parent].invalidate()


###############################################################################
class GraphNodeSettable(GraphNode):
    """
    Derived class used for nodes whose value can be explicitly set (such as
    Instreams and descriptors that implement a setter).
    """
    __slots__ = ("VT", "obj_ref", "parents",
                 "children", "valid", "value", "old_node")


###############################################################################
class GraphNodeCalc(GraphNode):
    """
    Derived class used for calculated callable ValueTypes.
    """
    __slots__ = ("VT", "obj_ref", "parents", "children",
                 "valid", "value", "old_node", "args", "kwds")

    ##-------------------------------------------------------------------------
    def __init__(self, VT, obj_ref):
        super().__init__(VT, obj_ref)
        self.args = ()
        self.kwds = {}

    ##-------------------------------------------------------------------------
    def get_value(self, *args, **kwds):
        # --- if args and kwds don't match stored values, the graph node is
        #     assumed no longer valid
        if args != self.args or kwds != self.kwds:
            self.valid = False
            self.args = args
            self.kwds = kwds

        if self.valid:
            return self.value
        else:
            # --- call the object's method with provided arguments
            self.value = getattr(self.obj_ref(), self.VT)(*args, **kwds)
            self.valid = True
            return self.value

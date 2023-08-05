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

from onyx.database.ufo_base import UfoBase
from onyx.database.objdb import ObjNotFound
from onyx.database.objdb_api import GetObj, DelObj
from onyx.depgraph.graph import DependencyGraph, CreateNode, GraphNodeSettable
from onyx.depgraph.graph import GraphNodeError

import onyx.database as onyx_db
import onyx.depgraph as onyx_dg

import functools

__all__ = [
    "UseGraph",
    "GraphNodeVt",
    "CreateInMemory",
    "RemoveFromGraph",
    "PurgeObj",
    "GetNode",
    "GetVal",
    "SetVal",
    "InvalidateNode",
    "NodesByObjName",
    "ValueTypesByInstance",
    "ChildrenIterator",
    "LeavesIterator",
    "SettableIterator",
]


###############################################################################
class UseGraph(object):
    """
    Context manager used to activate the dependency graph
    """
    def __init__(self, graph=None):
        self.graph = graph or DependencyGraph()

    def __enter__(self):
        self.current = onyx_dg.graph
        onyx_dg.graph = self.graph

    def __exit__(self, *args):
        onyx_dg.graph.clear()
        onyx_dg.graph = self.current
        # --- returns False so that all execptions raised will be propagated
        return False


###############################################################################
##  Base class for ValueTypes
class ValueType(object):
    pass


###############################################################################
class CalcVT(ValueType):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner=None):
        self.instance = instance
        return self

    def __set__(self, instance, value):
        raise AttributeError("Cannot set a Calc VT")

    def __call__(self, *args, **kwds):
        caller = (self.instance.Name, self.func.__name__)
        return self.func(self.instance,
                         functools.partial(GetNodeVal, caller), *args, **kwds)


###############################################################################
class SettableVT(ValueType):
    def __init__(self, fget, fset, name):
        # --- make sure that getter and setter functions have the following
        #     signature:
        #         fget(self, graph), fset(self, graph, value)
        #
        if fget.__code__.co_argcount < 2:
            raise GraphNodeError("Missing self and/or "
                                 "graph in the getter definition")
        if fget.__code__.co_argcount > 2:
            raise GraphNodeError("A Settable VT getter cannot take "
                                 "extra arguments besides self and graph")
        if fset.__code__.co_argcount < 3:
            raise GraphNodeError("Missing self and/or graph "
                                 "and/or value in the setter definition")
        if fset.__code__.co_argcount > 3:
            raise GraphNodeError("A Settable VT setter cannot take extra "
                                 "arguments besides self, graph, and value")
        self.fget = fget
        self.fset = fset
        self.__name__ = name

    def __get__(self, instance, owner=None):
        caller = (instance.Name, self.__name__)
        return self.fget(instance, functools.partial(GetNodeVal, caller))

    def __set__(self, instance, value):
        caller = (instance.Name, self.__name__)
        self.fset(instance, functools.partial(GetNodeVal, caller), value)


###############################################################################
class PropertyVT(ValueType):
    def __init__(self, fget):
        # --- make sure that the decorated method is of the type:
        #         f(self, graph)
        #
        if fget.__code__.co_argcount < 2:
            raise GraphNodeError("Missing self and/or "
                                 "graph in the method definition")
        if fget.__code__.co_argcount > 2:
            raise GraphNodeError("A Property VT cannot take "
                                 "extra arguments besides self and graph")
        self.fget = fget

    def __get__(self, instance, owner=None):
        caller = (instance.Name, self.fget.__name__)
        return self.fget(instance, functools.partial(GetNodeVal, caller))

    def __set__(self, instance, value):
        raise AttributeError("Cannot set a Property VT")


###############################################################################
class GraphNodeVt(object):
    """
    Calss-method decorator for objects derived from UfoBase.
    """
    ##-------------------------------------------------------------------------
    def __init__(self, vt_type="Calc", fget=None, fset=None):
        self.vt_type = vt_type
        if vt_type == "Settable":
            if fget is None or fset is None:
                raise GraphNodeError("Settable VT needs "
                                     "both getter and setter")
            else:
                self.fget = fget
                self.fset = fset

    ##-------------------------------------------------------------------------
    def __call__(self, func):
        if self.vt_type == "Calc":
            return CalcVT(func)
        elif self.vt_type == "Property":
            return PropertyVT(func)
        elif self.vt_type == "Settable":
            return SettableVT(self.fget, self.fset, func.__name__)
        else:
            GraphNodeError("Unrecognized VT type {0:s}".format(self.vt_type))


##-----------------------------------------------------------------------------
def CreateInMemory(instance):
    """
    Description:
        Helper function that creates an instance of an object derived from
        UfoBase in memory so that  all its VTs are on-graph and their values
        can be retrieved using the standard API (GetVal, GetNodeValue or graph
        when from within a mothod decorated by GraphNodeVt).
    Inputs:
        instance - an instance of an object derived from UfoBase
    Returns:
        The instance itself.
    """
    try:
        # --- return a reference to the cached instance with same name
        return onyx_dg.graph.objects[instance.Name]
    except KeyError:
        # --- add object instance to graph cache
        onyx_dg.graph.objects[instance.Name] = instance
        # --- add object instance to database weak references
        # FIXME: are we sure we need this???
        onyx_db.obj_clt.refs[instance.Name] = instance
        # --- return a reference to the instance
        return instance


##-----------------------------------------------------------------------------
def RemoveFromGraph(name):
    """
    Description:
        Remove all VTs of an object from the graph.
    Inputs:
        name - the name of an instance of an object derived from UfoBase
    Returns:
        None.
    """
    # --- make sure that name is indeed the object's Name
    if isinstance(name, UfoBase):
        name = name.Name

    # --- first remove from the graph all nodes referring to this object
    for node in NodesByObjName(name):
        # --- reconstruct node name
        node_name = (node.obj_ref().Name, node.VT)
        # --- invalidate parents and remove node from children list
        for parent in node.parents:
            onyx_dg.graph[parent].invalidate()
            onyx_dg.graph[parent].children.remove(node_name)
        # --- remove from parents list of each child
        for child in node.children:
            onyx_dg.graph[child].parents.remove(node_name)
        # --- remove node from the graph
        del onyx_dg.graph[node_name]

    # --- remove the object from the database cache (if present)
    # FIXME: are we sure we need this???
    del onyx_db.obj_clt[name]

    # --- finally remove the object itself from the graph's cache and
    #     VT mapping (if present)
    onyx_dg.graph.vts_by_obj.pop(name, None)
    onyx_dg.graph.objects.pop(name, None)


##-----------------------------------------------------------------------------
def PurgeObj(obj):
    """
    Description:
        Remove all VTs of an object from the graph and then delete it from
        the backend.
    Inputs:
        obj - an instance of an object derived from UfoBase (or its name)
    Returns:
        None.
    """
    RemoveFromGraph(obj)
    try:
        DelObj(obj)
    except ObjNotFound:
        pass


##-----------------------------------------------------------------------------
def GetNode(target):
    """
    Description:
        Helper function: Gets a GraphNode from the graph or creates it, if not
        present.
    Inputs:
        target - a (Object, VT) tuple
    Returns:
        A hard reference to the node in the graph.
    """
    try:
        return onyx_dg.graph[target]
    except KeyError:
        node = CreateNode(target)
        onyx_dg.graph[target] = node
        return node


##-----------------------------------------------------------------------------
def GetNodeVal(caller, obj, VT, *args, **kwds):
    """
    Description:
        This is the proper way of calling a VT on-graph. Use this method to
        get a value type from within a method that has been decorated by
        @GraphNodeVt().
    Inputs:
        caller - caller node identity
        obj    - target object as defined in database (or memory)
        VT     - target value type (an instream or a method of a ufo class
                 decorated by @GraphNodeVt())
        *args  - positional arguments used to call the target method
        **kwds -      named arguments used to call the target method
    Returns:
        The VT value.
    """
    # --- get the calling node from the graph (the node is created if it
    #     doesn't exsist)
    caller_node = GetNode(caller)

    # --- define target tuple (equivalent to the calling vti)
    if isinstance(obj, str):
        target = (obj, VT)
    else:
        target = (obj.Name, VT)

    # --- add target node name to its Children
    caller_node.children.add(target)
    # --- get the target node from the graph (the node is created if it
    #     doesn't exsist)
    target_node = GetNode(target)
    # --- add calling node to its Parents
    target_node.parents.add(caller)
    # --- now that the graph is set up, return target node value
    return target_node.get_value(*args, **kwds)


##-----------------------------------------------------------------------------
def GetVal(obj, VT, *args, **kwds):
    """
    Description:
        This is the proper way of calling a VT off-graph. Use this method to
        get a value type from a script.
    Inputs:
        obj    - target object in database (or memory)
        VT     - target value type (an instream or a method of a ufo class
                 decorated by @GraphNodeVt())
        *args  - positional arguments used to call the target method
        **kwds -      named arguments used to call the target method
    Returns:
        The VT value.
    """
    # --- make sure that obj is the object's Name
    if isinstance(obj, UfoBase):
        obj = obj.Name
    # --- return node value
    return GetNode((obj, VT)).get_value(*args, **kwds)


##-----------------------------------------------------------------------------
def SetVal(obj, VT, value):
    """
    Description:
        Set the value of an on-graph attribute (instream). When obj is
        persisted UpdateObj on obj.Name, the new attribute's value is
        persisted as well.
        NB: only leaf nodes (i.e. nodes that are object's instreams)
            can be set.
    Inputs:
        obj   - target object in database (or memory)
        VT    - target value type (an instream or a method of a ufo class
                 decorated by @GraphNodeVt())
        value - the value to set the VT to
    Returns:
        None.
    """
    # --- make sure that obj is the object's Name
    if isinstance(obj, UfoBase):
        obj = obj.Name

    # --- get the target node from the graph
    name = (obj, VT)
    node = GetNode(name)

    if not isinstance(node, GraphNodeSettable):
        raise GraphNodeError("({0:s},{1:s}) "
                             "is not a settable VT".format(*name))

    # --- remove this node from the set of parents of all its children
    for child in node.children:
        onyx_dg.graph[child].parents.remove(name)

    # --- remove all its children
    node.children = set()

    # --- invalidate all its parents
    for parent in node.parents:
        onyx_dg.graph[parent].invalidate()

    # --- set the node value and set its state to valid
    node.value = value
    node.valid = True

    # --- set attribute in the cached instance of the object
    setattr(node.obj_ref(), node.VT, node.value)


##-----------------------------------------------------------------------------
def InvalidateNode(obj, VT):
    """
    Description:
        Invalidate a node (defined by the tuple (obj, VT)) in the graph
        (if present).
    Inputs:
        obj - target object in database (or memory)
        VT  - target value type (an instream or a method of a ufo class
                 decorated by @GraphNodeVt())
    Returns:
        None.
    """
    if isinstance(obj, UfoBase):
        obj = obj.Name
    GetNode((obj, VT)).invalidate()


##-----------------------------------------------------------------------------
def NodesByObjName(name):
    """
    Description:
        Generator: returns all the nodes that reference the same object
    Inputs:
        name - target object's name in database (or memory)
    Yields:
        Graph nodes.
    """
    try:
        for VT in onyx_dg.graph.vts_by_obj[name]:
            yield onyx_dg.graph[(name, VT)]
    except KeyError:
        raise StopIteration


##-----------------------------------------------------------------------------
def ValueTypesByInstance(obj):
    """
    Description:
        Returns a list of all value types for object obj
    Inputs:
        obj - target object in database (or memory)
    Returns:
        A list of VT names.
    """
    if isinstance(obj, str):
        obj = GetObj(obj)

    cls = obj.__class__
    calc = [name for name, VT in
            cls.__dict__.items() if isinstance(VT, ValueType)]

    return list(obj.Instreams) + calc


##-----------------------------------------------------------------------------
def ChildrenIterator(obj, VT, child_VT, force_eval=True):
    """
    Description:
        Generator: returns all the children of a given node with a specific VT.
    Inputs:
        obj      - object in database (or memory)
        VT       - parent value type
        child_VT - children value type
    Yields:
        A list of object names.
    """
    if not isinstance(obj, str):
        obj = obj.Name

    # FIXME: have to evaluate this portion of the graph just to get its
    #        topology
    if force_eval:
        GetVal(obj, VT)

    for name, vt in onyx_dg.graph[(obj, VT)].children:
        if vt == child_VT:
            yield name
        else:
            for kid in ChildrenIterator(name, vt, child_VT, force_eval=False):
                yield kid


##-----------------------------------------------------------------------------
def LeavesIterator(obj, VT, force_eval=True):
    """
    Description:
        Generator: returns all leaf-level nodes (Instreams) of a given node.
    Inputs:
        obj - object in database (or memory)
        VT  - value type
    Yields:
        A list of nodes.
    """
    if not isinstance(obj, str):
        obj = obj.Name

    # FIXME: have to evaluate this portion of the graph just to get its
    #        topology
    if force_eval:
        GetVal(obj, VT)

    instreams = GetVal(obj, "Instreams")

    for name, vt in onyx_dg.graph[(obj, VT)].children:
        if vt in instreams:
            yield name, vt
        else:
            for leaf in LeavesIterator(name, vt, force_eval=False):
                yield leaf


##-----------------------------------------------------------------------------
def SettableIterator(obj, VT, force_eval=True):
    """
    Description:
        Generator: returns all settable children of a given node.
    Inputs:
        obj - object in database (or memory)
        VT  - value type
    Yields:
        A list of nodes.
    """
    if not isinstance(obj, str):
        obj = obj.Name

    # FIXME: have to evaluate this portion of the graph just to get its
    #        topology
    if force_eval:
        GetVal(obj, VT)

    for name, vt in onyx_dg.graph[(obj, VT)].children:
        node = onyx_dg.graph[(name, vt)]
        for leaf in SettableIterator(name, vt, force_eval=False):
            if leaf is not None:
                yield leaf

        if isinstance(node, GraphNodeSettable):
            yield name, vt

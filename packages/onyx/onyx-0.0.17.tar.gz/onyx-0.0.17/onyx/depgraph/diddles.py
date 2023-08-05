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
from onyx.depgraph.graph import GraphNodeError, GraphNodeCalc
from onyx.depgraph.graph_api import GetNode

import onyx.depgraph as onyx_dg

__all__ = ["SetDiddle", "EvalBlock", "DiddleScope"]


##-----------------------------------------------------------------------------
def SetDiddle(obj_name, VT, value, eval_block=None):
    """
    Description:
        Diddle the value of a ValueType. This is generally used withing an
        EvalBlock.
        NB: only Instreams and VTs defined as Property can be diddled.
    Inputs:
        obj_name   - target object in database (or memory)
        VT         - target value type (an Instream or a method decorated by
                     @GraphNodeVt)
        value      - the value to diddle the VT to
        eval_block - EvalBlock context manager
    Returns:
        None.
    """
    # --- make sure that obj is the object's Name
    if isinstance(obj_name, UfoBase):
        obj_name = obj_name.Name

    # --- get the target node from the graph
    name = (obj_name, VT)
    node = GetNode(name)

    # --- raise exception if VT cannot be diddled
    if isinstance(node, GraphNodeCalc):
        raise GraphNodeError("%s, %s: Only Instreams "
                             "and Properties can be diddled".format(name))

    # --- look for a valid (i.e. not used) node name for the old node
    idx = 0
    name_old = (obj_name, VT, idx)
    while name_old in onyx_dg.graph:
        idx += 1
        name_old = (obj_name, VT, idx)

    # --- clone original node and keep it on graph as name_old
    onyx_dg.graph[name_old] = node.clone()

    # --- save the name of the original node
    node.old_node = name_old

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

    # --- if present, add name of diddled node to the EvalBlock context manager
    if eval_block is not None:
        eval_block.append(name)


###############################################################################
class EvalBlock(object):
    """
    Description:
        Context manager used to manage lifetime of one or more one-off diddles.
    Usage:
        
    """
    ##-------------------------------------------------------------------------
    def __init__(self):
        self.__diddles = []

    def append(self, value):
        self.__diddles.append(value)

    ##-------------------------------------------------------------------------
    def __enter__(self):
        # --- return a reference to itself (to be used by SetDiddle)
        return self

    ##-------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        for obj_name, VT in reversed(self.__diddles):
            name = (obj_name, VT)
            name_old = onyx_dg.graph[name].old_node

            # --- invalidate all parents
            for parent in (onyx_dg.graph[name].parents |
                           onyx_dg.graph[name_old].parents):
                onyx_dg.graph[parent].invalidate()

            # --- reconstruct connection with children
            for child in onyx_dg.graph[name_old].children:
                onyx_dg.graph[child].parents.add(name)

            # --- recover original node from the graph
            onyx_dg.graph[name] = onyx_dg.graph[name_old]

            # --- remove original node from the graph
            del onyx_dg.graph[name_old]


###############################################################################
class DiddleScope(object):
    """
    Description:
        Context manager used to manage lifetime of diddles that will be used
        several times.
    Usage:
        
    """
    ##-------------------------------------------------------------------------
    def __init__(self):
        self.__active = False
        self.__diddles = []

    ##-------------------------------------------------------------------------
    def set_diddle(self, obj_name, VT, value):
        if isinstance(obj_name, UfoBase):
            obj_name = obj_name.Name
        if self.__active:
            SetDiddle(obj_name, VT, value)
        self.__diddles.append((obj_name, VT, value))

    ##-------------------------------------------------------------------------
    def __enter__(self):
        for obj, VT, value in self.__diddles:
            SetDiddle(obj, VT, value)
        self.__active = True
        return self

    ##-------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        for obj_name, VT, _ in reversed(self.__diddles):
            name = (obj_name, VT)
            name_old = onyx_dg.graph[name].old_node

            # --- invalidate all parents
            for parent in (onyx_dg.graph[name].parents |
                           onyx_dg.graph[name_old].parents):
                onyx_dg.graph[parent].invalidate()

            # --- reconstruct connection with children
            for child in onyx_dg.graph[name_old].children:
                onyx_dg.graph[child].parents.add(name)

            # --- recover original node from the graph
            onyx_dg.graph[name] = onyx_dg.graph[name_old]

            # --- remove original node from the graph
            del onyx_dg.graph[name_old]

        self.__active = False
        return False

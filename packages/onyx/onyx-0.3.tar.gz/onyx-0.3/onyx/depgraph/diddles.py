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
from onyx.depgraph.graph import GraphNodeError, GraphNodeCalc, DependencyGraph
from onyx.depgraph.graph_api import GetNode

import onyx.depgraph as onyx_dg
import copy

__all__ = ["EvalBlock", "DiddleScope"]


###############################################################################
class EvalBlock(object):
    """
    Description:
        Context manager used to manage lifetime of one or more one-off diddles.
    Usage:
        Typical usage is as follows:

            with EvalBlock() as eb:
                ...
                eb.set_diddle("abc", "xyz", 123)
                ...
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        self.__diddles = []
        self.__diddled_nodes = {}

    # -------------------------------------------------------------------------
    def __enter__(self):
        # --- return a reference to itself (to be used by set_diddle)
        return self

    # -------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        for node_def in reversed(self.__diddles):
            old_node = self.__diddled_nodes[node_def]

            # --- invalidate all parents, but not the node
            for parent in (onyx_dg.graph[node_def].parents | old_node.parents):
                onyx_dg.graph[parent].invalidate()

            # --- reconstruct connection with children
            for child in old_node.children:
                onyx_dg.graph[child].parents.add(node_def)

            # --- store pre-diddle node into the graph
            onyx_dg.graph[node_def] = old_node

    # -------------------------------------------------------------------------
    def set_diddle(self, obj_name, VT, value):
        """
        Description:
            Diddle the value of a ValueType within an EvalBlock.
            NB: only StoredAttrs and VTs defined as Property can be diddled.
        Inputs:
            obj_name - target object in database (or memory)
            VT       - target value type (an Instream or a method decorated by
                       @GraphNodeVt)
            value    - the value to diddle the VT to
        Returns:
            None.
        """
        if isinstance(obj_name, UfoBase):
            node_def = (obj_name.Name, VT)
        else:
            node_def = (obj_name, VT)

        # --- get the target node from the graph
        node = GetNode(node_def)

        # --- raise exception if VT cannot be diddled
        if isinstance(node, GraphNodeCalc):
            raise GraphNodeError("%s, %s: Only StoredAttrs and "
                                 "Properties can be diddled".format(node_def))

        # --- copy pre-diddle node and store it in __diddled_nodes. This only
        #     needs to be done the first time a VT is diddled.
        if node_def not in self.__diddled_nodes:
            self.__diddles.append(node_def)
            self.__diddled_nodes[node_def] = copy.deepcopy(node)

        # --- remove this node from the set of parents of all its children
        for child in node.children:
            onyx_dg.graph[child].parents.remove(node_def)

        # --- remove all its children
        node.children = set()

        # --- invalidate all its parents
        for parent in node.parents:
            onyx_dg.graph[parent].invalidate()

        # --- set the node value and set its state to valid
        node.value = value
        node.valid = True


###############################################################################
class DiddleScope(DependencyGraph):
    """
    Description:
        Context manager used to manage lifetime of diddles. Diddles set within
        a DiddleScope can be used several times.
    Usage:
        Typical usage is as follows:

            scope = DiddleScope()
            scope.set_diddle("abc", xyz", 123)
            with scope:
                ...
                scope.set_diddle("abc", "xxx", 666)
                ...

            with ds:
                ...
                ...
    """
    # -------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.active = False
        self.fallback = onyx_dg.graph

    # -------------------------------------------------------------------------
    def __enter__(self):
        if onyx_dg.graph is not self.fallback:
            raise ValueError("The active Graph has changed "
                             "since the DiddleScope was created.")
        self.active = True
        onyx_dg.graph = self

    # -------------------------------------------------------------------------
    def __exit__(self, *args):
        self.active = False
        onyx_dg.graph = self.fallback
        # --- returns False so that all execptions raised will be propagated
        return False

    # -------------------------------------------------------------------------
    def __getitem__(self, item):
        """
        Nodes that have not been explicitely copied into the diddle scope are
        shared with the fallback graph.
        """
        try:
            return super().__getitem__(item)
        except KeyError:
            return self.fallback[item]

    # -------------------------------------------------------------------------
    def copy_graph(self, node_def):
        """
        Recursively make a copy (if needed) of the portion of graph that
        depends on the current node.
        """
        try:
            node = super().__getitem__(node_def)
        except KeyError:
            try:
                self[node_def] = node = copy.deepcopy(self.fallback[node_def])
            except KeyError:
                # --- the trip stops here if the node doesn't exist in the
                #     fallback graph
                return

        for parent in node.parents:
            self.copy_graph(parent)

    # -------------------------------------------------------------------------
    def set_diddle(self, obj_name, VT, value):
        """
        Description:
            Diddle the value of a ValueType within a DiddleScope.
            NB: only StoredAttrs and VTs defined as Property can be diddled.
        Inputs:
            obj_name - target object in database (or memory)
            VT       - target value type (an Instream or a method decorated by
                       @GraphNodeVt)
            value    - the value to diddle the VT to
        Returns:
            None.
        """
        if not self.active:
            # --- switch graph to diddle scope
            onyx_dg.graph = self

        if isinstance(obj_name, UfoBase):
            node_def = (obj_name.Name, VT)
        else:
            node_def = (obj_name, VT)

        # --- make a copy of the graph that depends on node
        self.copy_graph(node_def)

        # --- get the target node from the graph
        node = GetNode(node_def)

        # --- raise exception if VT cannot be diddled
        if isinstance(node, GraphNodeCalc):
            raise GraphNodeError("({0:s}, {1:s}): Only StoredAttrs and "
                                 "Properties can be diddled".format(*node_def))

        # --- remove this node from the set of parents of all its children
        for child in node.children:
            self[child].parents.discard(node_def)

        # --- remove all its children
        node.children = set()

        # --- invalidate all its parents
        for parent in node.parents:
            self[parent].invalidate()

        # --- set the node value and set its state to valid
        node.value = value
        node.valid = True

        if not self.active:
            # --- switch graph back to the fallback
            onyx_dg.graph = self.fallback

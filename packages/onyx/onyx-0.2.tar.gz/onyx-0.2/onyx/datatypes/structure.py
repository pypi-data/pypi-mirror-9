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

import collections
import copy

__all__ = ["Structure", "StructureError"]


###############################################################################
class StructureError(Exception):
    """
    Base class for all Structure exceptions.
    """
    pass


###############################################################################
class Structure(collections.OrderedDict):
    """
     Inherits from ordered dictionary and implements addition and subtraction
     functionality.
    """
    # -------------------------------------------------------------------------
    #  addition methods

    def __iadd__(self, other):
        for key, value in other.items():
            self[key] = self.get(key, 0.0) + value
        return self

    def __add__(self, other):
        struct = copy.deepcopy(self)
        for key, value in other.items():
            struct[key] = struct.get(key, 0.0) + value
        return struct

    # -------------------------------------------------------------------------
    #  subtraction methods

    def __isub__(self, other):
        for key, value in other.items():
            self[key] = self.get(key, 0.0) - value
        return self

    def __sub__(self, other):
        struct = copy.deepcopy(self)
        for key, value in other.items():
            struct[key] = struct.get(key, 0.0) - value
        return struct

    # -------------------------------------------------------------------------
    #  addition and multiplication by scalars

    def __radd__(self, scalar):
        struct = copy.deepcopy(self)
        for key in struct:
            struct[key] += scalar
        return struct

    def __rmul__(self, scalar):
        struct = copy.deepcopy(self)
        for key in struct:
            struct[key] *= scalar
        return struct

    # -------------------------------------------------------------------------
    #  equality, order is not tested
    def __eq__(self, other):
        return dict.__eq__(self, other)

    # -------------------------------------------------------------------------
    def drop_zeros(self):
        """
        Drop items with zero value.
        """
        for key in self:
            if self[key] == 0.0:
                del self[key]

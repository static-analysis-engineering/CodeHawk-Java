# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2020 Kestrel Technology LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------

from chj.cost.CostBound import CostBound

from typing import cast, Optional, TYPE_CHECKING

import chj.util.fileutil as UF

if TYPE_CHECKING:
    from chj.cost.MethodCost import MethodCost
    from chj.index.JTerm import JTermRange

class CostMeasure():

    def __init__(self, methodcost: "MethodCost", cost: "JTermRange"):
        self.methodcost = methodcost                         # MethodCost
        self.costmodel = self.methodcost.costmodel           # CostModel
        self.cost = cost                                     # JTermRange
        self.lowerbounds = self.cost.get_lower_bounds()
        self.upperbounds = self.cost.get_upper_bounds()

    def get_value(self) -> int:
        if self.is_value():
            return self.cost.get_value()
        else:
            raise UF.CHJError(str(self) + " is not a value.")

    def get_lowerbound(self) -> int:
        if self.lowerbounds.is_constant(): return self.lowerbounds.get_jterms()[0].get_value()
        return 0

    def get_upperbound(self) -> int:
        if self.upperbounds.is_constant():
            return self.upperbounds.get_jterms()[0].get_value()
        else:
            raise UF.CHJError('Costmeasure ' + str(self) + ' does not have an upperbound')

    def get_ub_symbolic_dependencies(self):
        return self.cost.get_ub_symbolic_dependencies()

    def get_range(self):
        if self.cost.is_range(): return self.cost.get_range()
        if self.cost.is_float_range(): return self.cost.get_float_range()


    def is_unknown(self) -> bool: return self.cost.is_ub_open_range()

    def is_value(self) -> bool: return self.cost.is_value()

    def is_range(self) -> bool:
        return ((self.cost.is_range() or self.cost.is_float_range())
                    and not (self.is_value()))

    def has_lowerbound(self) -> bool:
        return self.lowerbounds.is_constant()

    def has_symbolic_bound(self) -> bool:
        return self.upperbounds.is_symbolic_expr()

    def get_symbolic_bound(self):
        return self.upperbounds.getsymbolicbound()

    def is_top (self) -> bool:
        return self.lowerbounds.is_top() and self.upperbounds.is_top()

    def __lt__(self, other: object) -> bool:
        if other is None or not isinstance(other, CostMeasure):
            return False
        if self.is_top(): return False
        if other.is_top(): return True
        if self.is_value():
            if other.is_value():
                return self.get_value() < other.get_value()
            if other.is_range():
                return self.get_value() < other.get_upperbound()
            if other.has_lowerbound():
                return self.get_value() < other.get_lowerbound()
            raise Exception()
        if self.is_range():
            if other.is_value(): return self.get_upperbound() < other.get_value()
            if other.is_range():
                if self.get_upperbound() == other.get_upperbound():
                    return self.get_lowerbound() < other.get_upperbound()
                return self.get_upperbound() < other.get_upperbound()
            if other.has_lowerbound():
                return self.get_upperbound() < other.get_lowerbound()
            raise Exception()
        if self.has_lowerbound():
            if other.is_value(): return self.get_lowerbound() < other.get_value()
            if other.is_range():
                return self.get_lowerbound() < other.get_lowerbound()
            if other.has_lowerbound():
                return self.get_lowerbound() < other.get_lowerbound()
            raise Exception()
        raise UF.CHJError('Failed to compare CostMeasures : ' + str(self) + ' and ' + str(other))

    def __eq__(self, other: object) -> bool:
        if other is None or not isinstance(other, CostMeasure): return False
        if self.is_top():
            return other.is_top()
        if self.is_value():
            return other.is_value() and self.get_value() == other.get_value()
        if self.is_range():
            return (other.is_range() and self.get_lowerbound() == other.get_lowerbound()
                    and self.get_upperbound() == other.get_upperbound())
        raise Exception()

    def __ne__(self, other: object) -> bool:
        if other is None or not isinstance(other, CostMeasure): return False
        return not self.__eq__(other)

    def __ge__(self, other: object) -> bool:
        if other is None or not isinstance(other, CostMeasure): return False
        return other.__lt__(self)

    def __le__(self, other: object) -> bool:
        if other is None or not isinstance(other, CostMeasure): return False
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: object) -> bool:
        if other is None or not isinstance(other, CostMeasure): return False
        return other.__le__(self)

    def __str__(self) -> str: return str(self.cost)
        

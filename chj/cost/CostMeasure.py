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

class CostMeasure():

    def __init__(self,methodcost,cost):
        self.methodcost = methodcost                         # MethodCost
        self.costmodel = self.methodcost.costmodel           # CostModel
        self.cost = cost                                     # JTermRange
        self.lowerbounds = self.cost.get_lower_bounds()
        self.upperbounds = self.cost.get_upper_bounds()

    def get_value(self):
        if self.is_value(): return self.cost.get_value()

    def get_lowerbound(self):
        if self.lowerbounds.is_value(): return self.lowerbounds[0].get_value()
        return 0

    def get_upperbound(self):
        if self.upperbounds.is_value(): return self.upperbounds[0].get_value()

    def get_ub_symbolic_dependencies(self):
        return self.cost.get_ub_symbolic_dependencies()

    def get_range(self):
        if self.cost.is_range(): return self.cost.get_range()
        if self.cost.is_float_range(): return self.cost.get_float_range()


    def is_unknown(self): return self.cost.is_ub_open_range()

    def is_value(self): return self.cost.is_value()

    def is_range(self):
        return ((self.cost.is_range() or self.cost.is_float_range())
                    and not (self.is_value()))

    def has_lowerbound(self):
        return self.lowerbounds.is_value()

    def has_symbolic_bound(self):
        return self.upperbounds.is_symbolic_bound()

    def get_symbolic_bound(self):
        return self.upperbounds.getsymbolicbound()

    def is_top (self):
        return self.lowerbounds.is_top() and self.upperbounds.is_top()

    def __lt__(self,other):
        if other is None: return False
        if self.is_top(): return False
        if other.is_top(): return True
        if self.is_value():
            if other.is_value(): return self.get_value() < other.get_value()
            if other.is_range(): return self.get_value() < other.get_upperbound()
            if other.haslowerbound(): return self.get_value() < other.get_lowerbound()
            raise Exception()
        if self.is_range():
            if other.is_value(): return self.get_upperbound() < other.get_value()
            if other.is_range(): 
                if self.get_upperbound() == other.get_upperbound():
                    return self.get_lowerbound() < other.get_lowerbound()
                return self.get_upperbound() < other.get_upperbound()
            if other.haslowerbound():
                return self.get_upperbound() < other.get_lowerbound()
            raise Exception()
        if self.haslowerbound():
            if other.is_value(): return self.get_lowerbound() < other.get_value()
            if other.is_range():
                return self.get_lowerbound() < other.get_lowerbound()
            if other.haslowerbound():
                return self.get_lowerbound() < other.get_lowerbound()
            raise Exception()
        raise Exception(str(self.xnode.attrib))

    def __eq__(self,other):
        if other is None: return False
        if self.istop():
            return other.istop()
        if self.is_value():
            return other.is_value() and self.get_value() == other.get_value()
        if self.is_range():
            return (other.is_range() and self.get_lowerbound() == other.get_lowerbound()
                    and self.get_upperbound() == other.get_upperbound())
        raise Exception()

    def __ne__(self,other): return not self.__eq__(other)

    def __ge__(self,other): return other.__lt__(self)

    def __le__(self,other): return self.__lt__(other) or self.__eq__(other)

    def __gt__(self,other): return other.__le__(self)                    

    def __str__(self): return str(self.cost)
        

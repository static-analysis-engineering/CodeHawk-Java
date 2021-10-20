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

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from chj.cost.CostModel import CostModel
    import chj.index.JTerm as JT

class CostBound():

    def __init__(self, costmodel: "CostModel", xnode: "ET.Element"):
        self.costmodel = costmodel       # CostModel
        self.jd = self.costmodel.jd      # DataDictionary
        self.xnode = xnode          # bounds node with bound node children
        self.terms: List[JT.JTermBase] = []
        self._initialize()

    def is_value(self) -> bool:
        return (any(x.is_value() for x in self.terms))

    def get_value(self):
        if self.is_value():
            for t in self.terms:
                if t.is_value(): return t.get_value()

    def is_symbolic_bound(self) -> bool:
        return (any(x.is_symbolic_value() for x in self.terms))

    def get_symbolic_bound(self) -> Optional["JT.JTermBase"]:
        if self.is_symbolic_bound():
            for t in self.terms:
                if t.is_symbolic_value(): return t

    def is_top(self) -> bool:
        return len(self.terms) == 0

    def __str__(self) -> str:
        if self.is_top(): return 'T'
        return '; '.join(str(t) for t in self.terms)

    def _initialize(self) -> None:
        bounds = self.xnode.findall('bound')
        if bounds is None or len(bounds) == 0: return
        for b in bounds:
            self.terms.append(JTerm(b))
            

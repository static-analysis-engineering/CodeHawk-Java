# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2020 Kestrel Technology LLC
# Copyright (c) 2021      Andrew McGraw
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

from chj.cost.CostMeasure import CostMeasure

import chj.util.fileutil as UF

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.cost.MethodCost import MethodCost
    import xml.etree.ElementTree as ET
    from chj.index.JTermDictionary import JTermDictionary

class LoopCost():

    def __init__(self, mc:"MethodCost", xnode:"ET.Element"):
        self.mc = mc                                # MethodCost
        self.jtd: "JTermDictionary" = mc.jtd        # JTermDictionary
        self.xnode = xnode
        self.one_iteration_cost: CostMeasure
        self.iteration_count: CostMeasure
        self._initialize()

    @property
    def pc(self) -> int:
        pc = self.xnode.get('hpc')
        if pc is None:
            raise UF.CHJError("hpc missing from xml")
        else:
            return int(pc)

    def _initialize(self) -> None:
        oneit = self.jtd.get_jterm_range(UF.safe_get(self.xnode, 'i1it', 'i1it missing from xml', int))
        itc = self.jtd.get_jterm_range(UF.safe_get(self.xnode, 'iitcount', 'iitcount missing from xml', int))
        self.one_iteration_cost = CostMeasure(self.mc,oneit)
        self.iteration_count = CostMeasure(self.mc,itc)

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

from chj.cost.CostMeasure import CostMeasure

import chj.util.fileutil as UF

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from chj.cost.CostModel import CostModel

class BlockCost():

    def __init__(self, costmodel: "CostModel", xnode: "ET.Element"):
        self.costmodel = costmodel
        self.xnode = xnode
        #self.pc = int(self.xnode.get('pc'))
        #self.cost = CostMeasure(self.costmodel, self.xnode.find('bcost'))

    @property
    def pc(self):
        pc = self.xnode.get('pc')
        if pc:
            return int(pc)
        else:
            raise UF.CHJError('PC of Block missing')

    @property
    def cost(self):
        bcost = self.xnode.find('bcost')
        if bcost:
            return CostMeasure(self.costmodel, bcost)
        else:
            raise UF.CHJError('BCost of Block missing')

    def __str__(self):
        return (str(self.pc) + ': ' + str(self.cost))

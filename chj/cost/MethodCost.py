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

from chj.cost.BlockCost import BlockCost
from chj.cost.CostMeasure import CostMeasure
from chj.cost.SideChannelCheck import SideChannelCheck
from chj.cost.LoopCost import LoopCost

import chj.util.fileutil as UF

from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from chj.app.JavaMethod import JavaMethod
    from chj.index.JTermDictionary import JTermDictionary
    from chj.cost.CostModel import CostModel
    from collections.abc import ValuesView
    from collections.abc import ItemsView

class MethodCost():

    def __init__(self, costmodel:"CostModel", xnode:"ET.Element"):
        self.costmodel = costmodel                              # CostModel
        self.xnode = xnode
        self.app = self.costmodel.app                           # AppAccess
        self.jtd: "JTermDictionary" = self.app.jd.jtd           # JTermDictionary
        self.blocks: Dict[int, CostMeasure] = {}                # pc -> CostMeasure
        self.loops: Dict[int, LoopCost] = {}                    # pc -> LoopCost
        self.sidechannelchecks: List[SideChannelCheck] = []     # SideChannelCheck list
        self.methodcost = CostMeasure (
            self,self.jtd.get_jterm_range(UF.safe_get(self.xnode, 'imcost', 'imcost missing from xml', int)))
        self._initialize()

    @property
    def cmsix(self) -> int:
        cmsix = self.xnode.get('cmsix')
        if cmsix is None:
            raise UF.CHJError("cmsix missing from xml")
        else:
            return int(cmsix)

    def get_method(self) -> "JavaMethod": return self.app.get_method(self.cmsix)

    def get_qname(self) -> str:
        return self.costmodel.jd.get_cms(self.cmsix).get_qname()

    def get_name(self) -> str:
        return self.costmodel.jd.get_cms(self.cmsix).methodname

    def get_block_costs(self) -> "ItemsView[int, CostMeasure]": return self.blocks.items()

    def get_block_cost(self, pc: int) -> CostMeasure:
        if pc in self.blocks: 
            return self.blocks[pc]
        else:
            raise UF.CHJError('Block cost at : ' + str(pc) + ' missing from xml')

    def get_simplified_block_cost(self, pc:int) -> str:
        cost = self.blocks[pc].cost
        if cost.is_value() or cost.is_range() or cost.is_top():
            return str(cost)
        else:
            return "X"

    def has_sidechannel_checks(self) -> bool: return len(self.sidechannelchecks) > 0

    def get_loop_costs(self) -> "ValuesView[LoopCost]" : return self.loops.values()

    def __str__(self) -> str:
        return (str(self.methodcost).ljust(60) + self.get_name() + ' (' +
                str(self.cmsix) + ')')

    def _initialize(self) -> None:
        xblocks = self.xnode.find('blocks')
        if not xblocks is None:
            for b in xblocks.findall('block'):
                pc = UF.safe_get(b, 'pc', 'pc missing from xml', int)
                jtrange = self.jtd.get_jterm_range(UF.safe_get(b, 'ibcost', 'ibcost missing from xml', int))
                bcost = CostMeasure(self,jtrange)
                self.blocks[pc] = bcost
        xscchecks = self.xnode.find('sidechannel-checks')
        if not xscchecks is None:
            for sc in xscchecks.findall('sc-check'):
                self.sidechannelchecks.append(SideChannelCheck(self, sc))
        xloops = self.xnode.find('loops')
        if not xloops is None:
            for l in UF.safe_find(self.xnode, 'loops', 'loops missing from xml').findall('loop'):
                pc = UF.safe_get(l, 'hpc', 'hpc missing from xml', int)
                lc = LoopCost(self,l)
                self.loops[pc] = lc
                
        
    

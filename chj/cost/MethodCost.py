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

class MethodCost ():

    def __init__(self,costmodel,xnode):
        self.costmodel = costmodel                 # CostModel
        self.xnode = xnode
        self.app = self.costmodel.app              # AppAccess
        self.jtd = self.app.jd.jtd                 # JTermDictionary
        self.cmsix = int(self.xnode.get('cmsix'))
        self.blocks = {}            # pc -> CostMeasure
        self.loops = {}             # pc -> LoopCost
        self.sidechannelchecks = [] # SideChannelCheck list
        self.methodcost = CostMeasure (
            self,self.jtd.get_jterm_range(int(self.xnode.get('imcost'))))
        self._initialize()

    def get_method(self): return self.app.get_method(self.cmsix)

    def get_qname(self):
        return self.costmodel.jd.get_cms(self.cmsix).get_qname()

    def get_name(self):
        return self.costmodel.jd.get_cms(self.cmsix).methodname

    def get_block_costs(self): return self.blocks.items()

    def get_block_cost(self,pc):
        if pc in self.blocks: return self.blocks[pc]

    def has_sidechannel_checks(self): return len(self.sidechannelchecks) > 0

    def get_loop_costs(self): return self.loops.values()

    def __str__(self):
        return (str(self.methodcost).ljust(60) + self.get_name() + ' (' +
                str(self.cmsix) + ')')

    def _initialize(self):
        xblocks = self.xnode.find('blocks')
        if not xblocks is None:
            for b in xblocks.findall('block'):
                pc = int(b.get('pc'))
                jtrange = self.jtd.get_jterm_range(int(b.get('ibcost')))
                bcost = CostMeasure(self,jtrange)
                self.blocks[pc] = bcost
        xscchecks = self.xnode.find('sidechannel-checks')
        if not xscchecks is None:
            for sc in xscchecks.findall('sc-check'):
                self.sidechannelchecks.append(SideChannelCheck(self, sc))
        xloops = self.xnode.find('loops')
        if not xloops is None:
            for l in self.xnode.find('loops').findall('loop'):
                pc = int(l.get('hpc'))
                lc = LoopCost(self,l)
                self.loops[pc] = lc
                
        
    

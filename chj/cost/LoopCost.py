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

class LoopCost():

    def __init__(self,mc,xnode):
        self.mc = mc               # MethodCost
        self.jtd = mc.jtd          # JTermDictionary
        self.xnode = xnode
        self.pc = int(xnode.get('hpc'))
        self.one_iteration_cost = None
        self.iteration_count = None
        self._initialize()

    def _initialize(self):
        oneit = self.jtd.get_jterm_range(int(self.xnode.get('i1it')))
        itc = self.jtd.get_jterm_range(int(self.xnode.get('iitcount')))
        self.one_iteration_cost = CostMeasure(self.mc,oneit)
        self.iteration_count = CostMeasure(self.mc,itc)

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

from chj.libsum.MethodSummarySignature import MethodSummarySignature
from chj.libsum.SummaryTimeCost import SummaryTimeCost

class MethodSummary(object):

    def __init__(self,classsum,xnode):
        self.classsum = jclasssum
        self.xnode = xnode

    def is_valid(self):
        return not ('valid' in self.xnode.attrib and self.xnode.get('valid') == 'no')

    def is_constructor(self): return False

    def is_inherited(self):
        return 'inherited' in self.xnode.attrib and self.xnode.get('inherited') == 'yes'

    def get_name(self): return self.xnode.get('name')

    def get_signature(self):
        return JMethodSummarySignature(self,self.xnode.find('signature'))

    def has_time_cost(self):
        return (not self.is_inherited()
                    and 'time-cost' in [ x.tag for x in self.xnode.find('summary') ])

    def get_time_cost(self):
        if self.has_time_cost():
            xtim = self.xnode.find('summary').find('time-cost')
            return JSummaryTimeCost(self,xtim)


class ConstructorSummary(MethodSummary):

    def __init__(self,classsum,xnode):
        JMethodSummary.__init__(self,classsum,xnode)

    def is_constructor(self): return True

    def is_inherited(self): return False

    def get_name(self): return '<init>'

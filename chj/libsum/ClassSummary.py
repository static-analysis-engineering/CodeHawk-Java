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

import chj.libsum.MethodSummary as MS

class ClassSummary(object):

    def __init__(self,jdkmodels,xnode):
        self.jdkmodels = jdkmodels
        self.xnode = xnode
        self.name = self.xnode.get('name')
        self.package = self.xnode.get('package')
        self.summaries = {}    # (name,signature-string) -> JMethodSummary
        self._initialize()

    def iter_method_summaries(self,f):
        for (name,ms) in self.summaries: f(name,ms,self.summaries[(name,ms)])

    def _initialize(self):
        xconstructors = self.xnode.find('constructors')
        if not xconstructors is None:
            for xm in self.xnode.find('constructors').findall('constructor'):
                c = MS.ConstructorSummary(self,xm)
                self.summaries[ (c.get_name(), str(c.get_signature())) ] = c
        for xm in self.xnode.find('methods').findall('method'):
            m = MS.MethodSummary(self,xm)
            self.summaries[ (m.get_name(), str(m.get_signature())) ] = m
        




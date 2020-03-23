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

import xml.etree.ElementTree as ET

import chj.util.fileutil as UF
import chj.util.xmlutil as UX

from chj.cost.MethodCost import MethodCost

class CostModel():

    def __init__(self,app):
        self.app = app            # AppAccess
        self.jd = self.app.jd     # DataDictionary
        self.methodcosts = {}     # cmsix -> MethodCost
        self.constants = {}       # name -> value
        self.originalconstants = {}
        self._initialize()

    def iter(self,f): 
        for m in sorted(self.methodcosts,key=lambda m:self.methodcosts[m]): 
            f(self.methodcosts[m])

    def reinitialize(self): self._initialize()

    def get_method_cost(self,id):
        if id in self.methodcosts: return self.methodcosts[id]

    def get_top_method_costs(self):
        result = []
        for cmsix in self.methodcosts:
            if self.methodcosts[cmsix].methodcost.cost.is_top():
                result.append(cmsix)
        return result

    def get_constant_method_costs(self):
        result = []
        for cmsix in self.methodcosts:
            if self.methodcosts[cmsix].methodcost.is_value():
                result.append((cmsix,self.methodcosts[cmsix].methodcost.get_value()))
        result = sorted(result,key=(lambda c : c[1]))
        return result

    def get_range_method_costs(self):
        result = []
        for cmsix in self.methodcosts:
            if (self.methodcosts[cmsix].methodcost.is_range()
                    and not self.methodcosts[cmsix].methodcost.is_value()):
                result.append((cmsix,self.methodcosts[cmsix].methodcost.get_range()))
        result = sorted(result,key=lambda x:x[1][1])
        return result

    def get_symbolic_method_costs(self):
        result = []
        for cmsix in self.methodcosts:
            cost = self.methodcosts[cmsix].methodcost
            if cost.is_top(): continue
            if cost.is_value(): continue
            if cost.is_range(): continue
            result.append((cmsix,cost))
        return result

    def get_constant_names(self): return self.constants.keys()

    def get_constant_values(self): return self.constants.items()

    def get_constant_value(self,name):
        if name in self.constants: return self.constants[name]

    def set_constant_value(self,name,v): self.constants[name] = v

    def get_unknown_methodcosts(self):
        return len(list(m for m in self.methodcosts
                        if self.methodcosts[m].get_method_cost().is_unknown()))
    
    def save_constants_file(self):
        doc = UX.dict_to_xmlpretty(self.constants,'constants','constant','name','value')
        if not doc is None:
            with open(UF.get_costmodel_constants_filename(self.app.path),'w') as fp:
                fp.write(doc)

    def restore_original_constants(self):
        for (name,value) in self.originalconstants.items():
            self.constants[name] = value

    def store_original_constants(self):
        xnode = UF.get_costmodel_constants_xnode(self.app.path)
        if not xnode is None:
            for x in xnode.findall('constant'):
                name = x.get('name')
                value = int(x.get('value'))
                self.originalconstants[name] = value
        else:
            print('No constants file found')

    def __str__(self):
        lines = []
        for m in self.methodcosts:
            lines.append(str(self.methodcosts[m]))
        unknowncount = sum( [ 1 for m in self.methodcosts if self.methodcosts[m].methodcost.is_unknown() ])
        lines.append('Methods with unknown cost: ' + str(unknowncount))
        return '\n'.join(lines)

    def _initialize(self):
        self.methodcosts = {}
        for cnix in self.jd.appclassindices.values():
            c = self.jd.get_cn(cnix)
            xnode = UF.get_costclass_xnode(self.app.path,c.get_package_name(),c.get_simple_name())
            if not xnode is None:
                for x in xnode.find('methods').findall('method'):
                    if 'abstract' in x.attrib: continue
                    if 'imcost' in x.attrib:
                        mc = MethodCost(self,x)
                        cmsix = int(x.get('cmsix'))
                        self.methodcosts[cmsix] = mc
                xcc = xnode.find('constructors')
                if not xcc is None:
                    for x in xcc.findall('constructor'):
                        mc = MethodCost(self,x)
                        self.methodcosts[mc.getid()] = mc



    

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


class Loop(object):

    def __init__(self,jmethod,xnode):
        self.jmethod = jmethod          # JavaMethod
        self.jd = jmethod.jd            # DataDictionary
        self.xnode = xnode
        self.depth = int(self.xnode.get('depth'))
        self.entry_pc = int(self.xnode.get('entry-pc'))
        self.first_pc = int(self.xnode.get('first-pc'))
        self.last_pc = int(self.xnode.get('last-pc'))
        self.instr_count = int(self.xnode.get('instrs'))
        self.jumpconditions = {}       # pc -> jumpcondition string
        self._initializejumpconditions()

    def get_max_iterations(self):
        result = []
        inode = self.xnode.find('max-iterations')
        if inode is None: 
            return result
        for jt in inode.findall('max-it'):
            result.append(self.jd.jtd.read_xml_jterm(jt))
        return result

    def get_constant_bounds(self):
        return [ x for x in self.get_max_iterations() if x.is_constant() ]

    def get_max_bound(self):
        if self.is_bounded():
            return (max([ int(str(x)) for x in self.get_constant_bounds() ]))

    def get_bound(self):
        if self.is_bounded():
            mxx = max([ int(str(x)) for x in self.get_constant_bounds() ])
            if mxx >= 2147483645: return 'MAX'
            return str(mxx)
        else:
            return '?'

    def is_bounded(self):
        consts = [ x for x in self.get_max_iterations() if x.is_constant() ]
        return (len(consts) > 0)

    def get_pc_jump_conditions(self): return self.jumpconditions.items()

    def _initializejumpconditions(self):
        for j in self.xnode.find('jump-conditions').findall('jump-cond'):
            self.jumpconditions[int(j.get('pc'))] = j.get('cond')

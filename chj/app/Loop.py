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

import chj.util.fileutil as UF

from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.index.JTerm import JTermBase
    from collections.abc import ItemsView
    import xml.etree.ElementTree as ET

class Loop(object):

    def __init__(self,jmethod: "JavaMethod", xnode: "ET.Element"):
        self.jmethod = jmethod          # JavaMethod
        self.jd = jmethod.jd            # DataDictionary
        self.xnode = xnode
        self.jumpconditions: Dict[int, str] = {}       # pc -> jumpcondition string
        self._initializejumpconditions()

    @property
    def depth(self) -> int:
        xdepth = self.xnode.get('depth')
        if xdepth is not None:
            return int(xdepth)
        else:
            raise UF.CHJError('depth missing from xml for loop in ' + self.jmethod.get_qname())

    @property
    def entry_pc(self) -> int:
        xentry_pc = self.xnode.get('entry-pc')
        if xentry_pc is not None:
            return int(xentry_pc)
        else:
            raise UF.CHJError('entry-pc missing from xml for loop in ' + self.jmethod.get_qname())

    @property
    def first_pc(self) -> int:
        xfirst_pc = self.xnode.get('first-pc')
        if xfirst_pc is not None:
            return int(xfirst_pc)
        else:
            raise UF.CHJError('first-pc missing from xml for loop in ' + self.jmethod.get_qname())

    @property
    def last_pc(self) -> int:
        xlast_pc = self.xnode.get('last-pc')
        if xlast_pc is not None:
            return int(xlast_pc)
        else:
            raise UF.CHJError('last-pc missing from xml for loop in ' + self.jmethod.get_qname())

    @property
    def instr_count(self) -> int:
        xinstr_count = self.xnode.get('instrs')
        if xinstr_count is not None:
            return int(xinstr_count)
        else:
            raise UF.CHJError('instrs missing from xml for loop in ' + self.jmethod.get_qname())

    def get_max_iterations(self) -> List["JTermBase"]:
        result: List["JTermBase"] = []
        inode = self.xnode.find('max-iterations')
        if inode is None: 
            return result
        for jt in inode.findall('max-it'):
            result.append(self.jd.jtd.read_xml_jterm(jt))
        return result

    def get_constant_bounds(self) -> List["JTermBase"]:
        return [ x for x in self.get_max_iterations() if x.is_constant() ]

    def get_max_bound(self) -> int:
        if self.is_bounded():
            return (max([ int(str(x)) for x in self.get_constant_bounds() ]))
        raise UF.CHJError("Loop is not bounded")

    def get_bound(self) -> str:
        if self.is_bounded():
            mxx = max([ int(str(x)) for x in self.get_constant_bounds() ])
            if mxx >= 2147483645: return 'MAX'
            return str(mxx)
        else:
            return '?'

    def is_bounded(self) -> bool:
        consts = [ x for x in self.get_max_iterations() if x.is_constant() ]
        return (len(consts) > 0)

    def get_pc_jump_conditions(self) -> "ItemsView[int, str]": return self.jumpconditions.items()

    def _initializejumpconditions(self) -> None:
        errormsg = ' missing from xml for loop in method ' + self.jmethod.get_qname()
        xjump = UF.safe_find(self.xnode, 'jump-conditions', 'jump-conditions' + errormsg)
        for j in xjump.findall('jump-cond'):
            self.jumpconditions[UF.safe_get(j, 'pc', 'pc' + errormsg, int)] = UF.safe_get(j, 'cond', 'cond' + errormsg, str)

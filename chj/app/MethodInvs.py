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

from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.index.JTerm import JTRelationalExpr
    import xml.etree.ElementTree as ET

import chj.util.fileutil as UF

class MethodInvs(object):

    def __init__(self, jmethod: "JavaMethod", xnode: "ET.Element"):
        self.jmethod = jmethod            # JavaMethod
        self.jtd = jmethod.jd.jtd         # JTermDictionary
        self.xnode = xnode
        self.invariants: Dict[int, List["JTRelationalExpr"]] = {}   # pc -> RelationalExpr list
        self._initialize()

    def __str__(self) -> str:
        lines = []
        for pc in sorted(self.invariants):
            invs = '; '.join([ str(x) for x in self.invariants[pc] ])
            lines.append(str(pc).rjust(5) + '  ' + invs)
        return '\n'.join(lines)
            
    def _initialize(self) -> None:
        if len(self.invariants) > 0: return
        for pnode in self.xnode.findall('pc-invs'):
            pc = UF.safe_get(pnode, 'pc', 'pc missing from xml for method invariants in ' + self.jmethod.get_qname(), int)
            inv = self.jtd.read_xml_relational_expr_list(pnode).get_exprs()
            self.invariants[pc] = inv

            
            

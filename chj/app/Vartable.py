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

import chj.util.fileutil as UF

from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.index.JType import StringConstant
    import xml.etree.ElementTree as ET

class VartableSlot():

    def __init__(self,
            vartable: "Vartable",
            xnode: "ET.Element"):
        self.jd = vartable.jd
        self.xnode = xnode
        self.tpd  = self.jd.tpd           # JTypeDictionary
        self.vartable = vartable
        self.name = self._name
        self.namelen = self.name.get_string_length()

    @property
    def _name(self) -> "StringConstant":
        name = self.xnode.get('iname')
        if name is not None:
            return self.tpd.get_string(int(name))
        else:
            raise UF.CHJError('iname missing for xml of vartable of method ' + self.vartable.jmethod.get_qname())

    @property
    def vtype(self):
        vtype = self.xnode.get('ivty')
        if vtype is not None:
            return self.tpd.get_value_type(int(vtype))
        else:
            raise UF.CHJError('ivty missing for xml of vartable of method ' + self.vartable.jmethod.get_qname())

    @property
    def vix(self) -> int:
        vix = self.xnode.get('vix')
        if vix is not None:
            return int(vix)
        else:
            raise UF.CHJError('vix missing for xml of vartable of method ' + self.vartable.jmethod.get_qname())

    @property
    def startpc(self) -> int:
        startpc = self.xnode.get('spc')
        if startpc is not None:
            return int(startpc)
        else:
            raise UF.CHJError('spc missing for xml of vartable of method ' + self.vartable.jmethod.get_qname())

    @property
    def endpc(self) -> int:
        endpc = self.xnode.get('endpc')
        if endpc is not None:
            return int(endpc)
        else:
            raise UF.CHJError('endpc missing for xml of vartable of method ' + self.vartable.jmethod.get_qname())

    def to_string(self, namelen: int) -> str:
        return (str(self.vix) + ' ' + str(self.name).ljust(namelen) + ' '
                    + str(self.startpc).rjust(5) + ' ' + str(self.endpc).rjust(5))
    
    def __str__(self) -> str:
        return str(self.vix) + ' ' + str(self.name) + ' ' + str(self.startpc) + ' ' + str(self.endpc)


class Vartable():
    '''Variable table (only available if compiled with debug).'''

    def __init__(self,
            jmethod: "JavaMethod",
            xnode: "ET.Element"):
        self.jmethod = jmethod           # JavaMethod
        self.jd = jmethod.jd             # DataDictionary
        self.xnode = xnode
        self.table: Dict[Tuple[int, int], VartableSlot] = {}                  # (index,startpc) -> VartableSlot
        self._initializetable()
        
    def getparameters(self) -> Dict[int, VartableSlot]:
        '''a variable is a parameter if its start pc equals 0.'''
        result = {}
        for (ix,sp) in self.table:
            if sp == 0: result[ix] = self.table[(ix,sp)]
        return result

    def __str__(self) -> str:
        lines = []
        lines.append('Variable table')
        lines.append('-' * 64)
        if len(self.table) > 0:
            maxlen = max (s.namelen for s in self.table.values())
            for s in sorted(self.table):
                lines.append(self.table[s].to_string(maxlen))
        lines.append('-' * 64)
        return '\n'.join(lines)

    def get_name(self, index: int, pc: int) -> str:
        for (ix,spc) in self.table:
            if ix == index and pc >= spc and pc <= self.table[(ix,spc)].endpc:
                return self.table[(ix,spc)].name.get_string()

    def _initializetable(self) -> None:
        for s in self.xnode.findall('slot'):
            vix = UF.safe_get(s, 'vix', 'vix missing from xml for slot of method ' + self.jmethod.get_qname(), int)
            spc = UF.safe_get(s, 'spc', 'spc missing from xml for slot of method ' + self.jmethod.get_qname(), int)
            index = (vix, spc)
            self.table[index] = VartableSlot(self,s)

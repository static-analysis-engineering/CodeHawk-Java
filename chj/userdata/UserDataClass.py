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

import xml.etree.ElementTree as ET

import chj.util.fileutil as UF
import chj.util.xmlutil as UX

from typing import Dict, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.index.AppAccess import AppAccess
    import xml.etree.ElementTree as ET

class UserDataClass(object):

    def __init__(self, app: "AppAccess", xnode: "ET.Element"):
        self.app = app
        self.xnode = xnode
        self.methods: Dict[int, "UserDataMethod"] = {}             # msix -> UserDataMethod
        self._initialize()

    @property
    def name(self) -> str:
        name = self.xnode.get('name')
        if name is not None:
            return str(name)
        else:
            raise UF.CHJError("name missing from xml for UserDataClass")

    @property
    def package(self) -> str:
        package = self.xnode.get('package')
        if package is not None:
            return str(package)
        else:
            raise UF.CHJError("package missing from xml for UserDataClass")

    def has_method(self, msix: int) -> bool:
        return msix in self.methods

    def get_method(self, msix: int) -> "UserDataMethod":
        if msix in self.methods:
            return self.methods[msix]
        raise UF.CHJError("Method " + str(msix) + " missing from UserDataClass " + self.name)

    def mk_method(self,
            name: str,
            msig: str,
            msix: int) -> None:
        if not msix in self.methods:
            print(self.__str__())
            print('Make method for ' + name + ' (' +  str(msix) + ')')
            self.methods[msix] = UserDataMethod(self,name,msig,msix)

    def write_xml(self, cnode: ET.Element) -> None:
        cnode.set('name',self.name)
        cnode.set('package',self.package)
        mmnode = ET.Element('methods')
        cnode.append(mmnode)
        for m in self.methods.values():
            mnode = ET.Element('method')
            m.write_xml(mnode)
            mmnode.append(mnode)

    def save_xml(self) -> None:
        root = UX.get_xml_header('class')
        cnode = ET.Element('class')
        self.write_xml(cnode)
        root.append(cnode)
        UF.save_userdataclass_file(self.app.path,self.package,self.name,root)

    def __str__(self) -> str:
        lines = []
        lines.append('Userdata for: ' + self.package + '.' + self.name)
        for m in self.methods:
            lines.append(str(m) +  ': ' + str(self.methods[m]))
        return '\n'.join(lines)

    def _initialize(self) -> None:
        if self.xnode is None: return
        methods = UF.safe_find(self.xnode, 'methods', 'methods missing from xml for UserDataClass')
        for mnode in methods.findall('method'):
            msig = UF.safe_get(mnode, 'sig', 'sig missing from xml for UserDataClass', str)
            mname = UF.safe_get(mnode, 'name', 'name missing from xml for UserDataClass', str)
            msix = self.app.jd.get_msix(mname, msig)
            m = UserDataMethod(self, mname, msig, msix)
            self.methods[msix] = m
            self._initialize_method(m, mnode)

    def _initialize_method(self, m: "UserDataMethod", mnode: "ET.Element") -> None:
        iinode = mnode.find('interface-targets')
        ccnode = mnode.find('callees')
        bbnode = mnode.find('bounds')
        mcnode = mnode.find('method-cost')
        errormsg = ' missing from xml for UserDataMethod: ' + self.name
        if not mcnode is None:
            mcost = []
            if 'iconst' in mcnode.attrib:
                mcost.append(('iconst', UF.safe_get(mcnode, 'iconst', 'iconst' + errormsg, int)))
            if 'lb' in mcnode.attrib:
                mcost.append(('lb', UF.safe_get(mcnode, 'lb', 'lb' + errormsg, int)))
            if 'ub' in mcnode.attrib:
                mcost.append(('ub', UF.safe_get(mcnode, 'ub', 'ub' + errormsg, int)))
            if len(mcost) > 0:
                m.add_method_cost(mcost)
        if not iinode is None:
            for inode in iinode.findall('tgt'):
                intf = UF.safe_get(inode, 'i', 'i' + errormsg, str)
                intftgt = UF.safe_get(inode, 't', 't' + errormsg, str)
                m.add_interface_target(intf, intftgt)
        if not ccnode is None:
            for cnode in ccnode.findall('callee'):
                kind = cnode.get('kind')
                if kind == 'restrict':
                    pc = UF.safe_get(cnode, 'pc', 'pc' + errormsg, int)
                    tgt = UF.safe_get(cnode, 'class', 'class' + errormsg, str)
                    m.add_callee_restriction(pc,tgt)
        if not bbnode is None:
            for bnode in bbnode.findall('loop'):
                pc = UF.safe_get(bnode, 'pc', 'pc' + errormsg, int)
                if 'it' in bnode.attrib:
                    boundtype = 'it'
                    numboundvalue = UF.safe_get(bnode, 'it', 'it' + errormsg, int)
                    m.add_numeric_bound(pc, numboundvalue)
                elif 'itc' in bnode.attrib:
                    boundtype = 'itc'
                    symboundvalue = UF.safe_get(bnode, 'itc', 'itc' + errormsg, str)
                    m.add_symbolic_bound(pc, symboundvalue)
                else:
                    print('*' * 80)
                    print('Error in reading bounds: no boundtype found')
                    print('*' * 80)
                    exit(1)

class UserDataMethod(object):

    def __init__(self, 
            userclass: UserDataClass,
            name: str,
            msig: str,
            msix: int):
        self.userclass = userclass
        self.msig = msig
        self.name = name
        self.calleerestrictions: Dict[int, str] = {}
        self.numericbounds: Dict[int, int] = {}
        self.symbolicbounds: Dict[int, str] = {}
        self.interfacerestrictions: Dict[str, str] = {}
        self.mcost: List[Tuple[str, int]] = []

    def add_interface_target(self, intf: str, tgt: str) -> None:
        self.interfacerestrictions[intf] = tgt

    def add_callee_restriction(self, pc: int, tgt: str) -> None:
        self.calleerestrictions[pc] = tgt

    def add_interface_restriction(self, interface: str, tgtclass: str) -> None:
        self.interfacerestrictions[interface] = tgtclass

    def add_numeric_bound(self, pc: int, boundvalue: int) -> None:
        self.numericbounds[pc] = boundvalue

    def add_symbolic_bound(self, pc: int, boundvalue: str) -> None:
        self.symbolicbounds[pc] = boundvalue

    def add_method_cost(self, mcost: List[Tuple[str, int]]) -> None:    # [ (attr-name,value) ]
        self.mcost = mcost

    def write_xml(self, mnode: "ET.Element") -> None:
        mnode.set('name',self.name)
        mnode.set('sig',self.msig)
        if len(self.mcost) > 0:
            mcnode = ET.Element('method-cost')
            mnode.append(mcnode)
            for (attr,attrval) in self.mcost:
                mcnode.set(attr,str(attrval))
        if len(self.interfacerestrictions) > 0:
            iinode = ET.Element('interface-targets')
            mnode.append(iinode)
            for (intf,tgt) in self.interfacerestrictions.items():
                inode = ET.Element('tgt')
                inode.set('i',intf)
                inode.set('t',tgt)
                iinode.append(inode)
        ccnode = ET.Element('callees')
        mnode.append(ccnode)
        for (pc,tgt) in self.calleerestrictions.items():
            cnode = ET.Element('callee')
            cnode.set('pc',str(pc))
            cnode.set('kind','restrict')
            cnode.set('class',tgt)
            ccnode.append(cnode)
        bbnode = ET.Element('bounds')
        mnode.append(bbnode)
        for (pc,numbound) in self.numericbounds.items():
            bnode = ET.Element('loop')
            bnode.set('pc',str(pc))
            bnode.set('it',str(numbound))
            bbnode.append(bnode)
        for (pc,symbound) in self.symbolicbounds.items():
            bnode = ET.Element('loop')
            bnode.set('pc',str(pc))
            bnode.set('itc',symbound)
            bbnode.append(bnode)

    def __str__(self) -> str:
        lines = []
        lines.append(' ')
        lines.append('  Method ' + self.name + ' ' +  self.msig)
        if len(self.interfacerestrictions) > 0:
            lines.append('  Interface restrictions:')
            for (intf,tgt) in self.interfacerestrictions.items():
                lines.append('  ' + intf + ' -> ' + tgt)
        if len(self.calleerestrictions) > 0:
            lines.append('  Callee restrictions:')
            for pc in sorted(self.calleerestrictions):
                lines.append('      ' + str(pc).rjust(4) + ': ' + self.calleerestrictions[pc])
        if len(self.numericbounds) > 0:
            lines.append('  Numeric bounds:')
            for pc in sorted(self.numericbounds):
                lines.append('      ' + str(pc).rjust(4) + ': ' + str(self.numericbounds[pc]))
        if len(self.symbolicbounds) > 0:
            lines.append('  Symbolic bounds:')
            for pc in sorted(self.symbolicbounds):
                lines.append('      ' + str(pc).rjust(4) + ': ' +  str(self.symbolicbounds[pc]))
        return '\n'.join(lines)
        


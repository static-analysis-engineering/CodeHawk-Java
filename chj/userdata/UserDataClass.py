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

class UserDataClass(object):

    def __init__(self,app,xnode):
        self.app = app
        self.xnode = xnode
        self.package = self.xnode.get('package')
        self.name = self.xnode.get('name')
        self.methods = {}             # msix -> UserDataMethod
        self._initialize()

    def has_method(self,msix):
        return msix in self.methods

    def get_method(self,msix):
        if msix in self.methods:
            return self.methods[msix]

    def mk_method(self,name,msig,msix):
        if not msix in self.methods:
            print(self.__str__())
            print('Make method for ' + name + ' (' +  str(msix) + ')')
            self.methods[msix] = UserDataMethod(self,name,msig,msix)

    def write_xml(self,cnode):
        cnode.set('name',self.name)
        cnode.set('package',self.package)
        mmnode = ET.Element('methods')
        cnode.append(mmnode)
        for m in self.methods.values():
            mnode = ET.Element('method')
            m.write_xml(mnode)
            mmnode.append(mnode)

    def save_xml(self):
        root = UX.get_xml_header('class')
        cnode = ET.Element('class')
        self.write_xml(cnode)
        root.append(cnode)
        UF.save_userdataclass_file(self.app.path,self.package,self.name,root)

    def __str__(self):
        lines = []
        lines.append('Userdata for: ' + self.package + '.' + self.name)
        for m in self.methods:
            lines.append(str(m) +  ': ' + str(self.methods[m]))
        return '\n'.join(lines)

    def _initialize(self):
        if self.xnode is None: return
        for mnode in self.xnode.find('methods').findall('method'):
            msig = mnode.get('sig')
            mname = mnode.get('name')
            msix = self.app.jd.get_msix(mname,msig)
            m = UserDataMethod(self,mname,msig,msix)
            self.methods[msix] = m
            self._initialize_method(m,mnode)

    def _initialize_method(self,m,mnode):
        ccnode = mnode.find('callees')
        bbnode = mnode.find('bounds')
        if not ccnode is None:
            for cnode in ccnode.findall('callee'):
                kind = cnode.get('kind')
                if kind == 'restrict':
                    pc = int(cnode.get('pc'))
                    tgt = cnode.get('class')
                    m.add_callee_restriction(pc,tgt)
        if not bbnode is None:
            for bnode in bbnode.findall('loop'):
                pc = int(bnode.get('pc'))
                if 'it' in bnode.attrib:
                    boundtype = 'it'
                    boundvalue = int(bnode.get('it'))
                elif 'itc' in bnode.attrib:
                    boundtype = 'itc'
                    boundvalue = bnode.get('itc')
                else:
                    print('*' * 80)
                    print('Error in reading bounds: no boundtype found')
                    print('*' * 80)
                    exit(1)
                m.add_bound(pc,boundtype,boundvalue)
        
        



class UserDataMethod(object):

    def __init__(self,userclass,name,msig,msix):
        self.userclass = userclass
        self.msig = msig
        self.name = name
        self.calleerestrictions = {}
        self.numericbounds = {}
        self.symbolicbounds = {}

    def add_callee_restriction(self,pc,tgt):
        self.calleerestrictions[pc] = tgt

    def add_bound(self,pc,boundtype,boundvalue):
        if boundtype == 'it':
            self.numericbounds[pc] = boundvalue
        else:
            self.symbolicbounds[pc] = boundvalue

    def write_xml(self,mnode):
        mnode.set('name',self.name)
        mnode.set('sig',self.msig)
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
        for (pc,bound) in self.numericbounds.items():
            bnode = ET.Element('loop')
            bnode.set('pc',str(pc))
            bnode.set('it',str(bound))
            bbnode.append(bnode)
        for (pc,bound) in self.symbolicbounds.items():
            bnode = ET.Element('loop')
            bnode.set('pc',str(pc))
            bnode.set('itc',bound)
            bbnode.append(bnode)

    def __str__(self):
        lines = []
        lines.append(' ')
        lines.append('  Method ' + self.name + ' ' +  self.msig)
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
        


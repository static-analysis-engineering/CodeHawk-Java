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


class VartableSlot():

    def __init__(self,vartable,xnode):
        self.jd = vartable.jd
        self.tpd  = self.jd.tpd           # JTypeDictionary
        self.vartable = vartable
        self.name = self.tpd.get_string(int(xnode.get('iname')))
        self.namelen = self.name.get_string_length()
        self.vix = int(xnode.get('vix'))
        self.vtype = self.tpd.get_value_type(int(xnode.get('ivty')))
        self.startpc = int(xnode.get('spc'))
        self.endpc = int(xnode.get('epc'))

    def to_string(self,namelen):
        return (str(self.vix) + ' ' + str(self.name).ljust(namelen) + ' '
                    + str(self.startpc).rjust(5) + ' ' + str(self.endpc).rjust(5))
    
    def __str__(self):
        return str(self.vix) + ' ' + str(self.name) + ' ' + str(self.startpc) + ' ' + str(self.endpc)


class Vartable():
    '''Variable table (only available if compiled with debug).'''

    def __init__(self,jmethod,xnode):
        self.jmethod = jmethod           # JavaMethod
        self.jd = jmethod.jd             # DataDictionary
        self.xnode = xnode
        self.table = {}                  # (index,startpc) -> VartableSlot
        self._initializetable()
        
    def getparameters(self):
        '''a variable is a parameter if its start pc equals 0.'''
        result = {}
        for (ix,sp) in self.table:
            if sp == 0: result[ix] = self.table[(ix,sp)]
        return result

    def __str__(self):
        lines = []
        lines.append('Variable table')
        lines.append('-' * 64)
        if len(self.table) > 0:
            maxlen = max (s.namelen for s in self.table.values())
            for s in sorted(self.table):
                lines.append(self.table[s].to_string(maxlen))
        lines.append('-' * 64)
        return '\n'.join(lines)

    def get_name(self,index,pc):
        for (ix,spc) in self.table:
            if ix == index and pc >= spc and pc <= self.table[(ix,spc)].endpc:
                return self.table[(ix,spc)].name

    def _initializetable(self):
        for s in self.xnode.findall('slot'):
            index = (int(s.get('vix')),int(s.get('spc')))
            self.table[index] = VartableSlot(self,s)

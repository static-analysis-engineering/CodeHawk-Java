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

from chj.libsum.SummaryValueType import SummaryValueType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from chj.libsum.MethodSummary import MethodSummary

class MethodSummarySignature(object):

    def __init__(self,
            methodsum: "MethodSummary",
            xnode: "ET.Element"):
        self.methodsum = methodsum
        self.xnode = xnode
        self.argtypes = [ SummaryValueType(x) for x in self.xnode.findall('arg') ]
        self.returntype = None
        xreturn = self.xnode.find('return')
        if not xreturn is None:
            self.returntype = SummaryValueType(xreturn)
        

    def __str__(self) -> str:
        sreturn = 'V' if self.returntype is None else str(self.returntype)
        return '(' + ''.join( [ str(t) for t in self.argtypes ]) + ')' + sreturn
        

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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET

basic_type_symbols = {
    "boolean": "Z",
    "byte": "B",
    "char": "C",
    "double": "D",
    "float": "F",
    "int": "I",
    "long": "L",
    "short": "S",
    "void": "V"
    }

class SummaryValueType(object):

    def __init__(self, xnode: "ET.Element") -> None:
        self.xnode = xnode

    def is_object(self) -> bool:
        return self.xnode[0].tag == 'object' or self.xnode[0].tag == 'new-object'

    def is_array(self) -> bool:
        return self.xnode[0].tag == 'array'

    def get_array_element_type(self) -> "SummaryValueType":
        return SummaryValueType(UF.safe_find(self.xnode, 'array', 'array missing from summaryvaluetype xml'))

    def is_basic_type(self) -> bool: 
        return not (self.is_object() or self.is_array())

    def __str__(self) -> str:
        if self.is_object():
            xtext = self.xnode[0].text
            if xtext is not None:
                cname = xtext.replace('.','/')
            else:
                raise UF.CHJError('summary value missing from xml')
            return 'L' + cname + ';'
        if self.is_array():
            return '[' + str(self.get_array_element_type())
        return basic_type_symbols[self.xnode[0].tag]
                                 
            

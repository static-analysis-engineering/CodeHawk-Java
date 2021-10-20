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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.index.DataDictionary import DataDictionary
    from chj.index.FieldSignature import FieldSignature
    from chj.app.JavaClass import JavaClass
    import xml.etree.ElementTree as ET

class Field():

    def __init__(self, jclass: "JavaClass", xnode: "ET.Element"):
        self.jclass = jclass                                        # JavaClass
        self.jd: "DataDictionary" = jclass.app.jd                   # DataDictionary
        self.cfsix = UF.safe_get(xnode, 'cfsix', 'cfsix missing from xml of class ' + jclass.get_qname(), int)
        self.access = xnode.get('access')
        self.isfinal = 'final' in xnode.attrib and xnode.get('final') == 'yes'
        self.isstatic = 'static' in xnode.attrib and xnode.get('static') == 'yes'
        self.xnode = xnode

    def get_signature(self) -> "FieldSignature":
        return self.jd.get_cfs(self.cfsix).get_signature()

    def get_field_name(self) -> str:
        return self.get_signature().get_name()

    def has_value(self) -> bool:
        v = self.xnode.find('value')
        return (not v is None)

    def is_scalar(self) -> bool: return self.get_signature().is_scalar()

    def is_array(self) -> bool: return self.get_signature().is_array()

    def is_object(self) -> bool: return self.get_signature().is_object()

    

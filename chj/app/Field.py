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

class Field():

    def __init__(self,jclass,xnode):
        self.jclass = jclass                     # JavaClass
        self.jd = jclass.app.jd                  # DataDictionary
        self.cfsix = int(xnode.get('cfsix'))
        self.access = xnode.get('access')
        self.isfinal = 'final' in xnode.attrib and xnode.get('final') == 'yes'
        self.isstatic = 'static' in xnode.attrib and xnode.get('static') == 'yes'
        self.xnode = xnode

    def get_signature(self):
        return self.jd.get_cfs(self.cfsix).get_signature()

    def get_field_name(self):
        return self.get_signature().get_name()

    def has_value(self):
        v = self.xnode.find('value')
        return (not v is None)

    def is_scalar(self): return self.get_signature().is_scalar()

    def is_array(self): return self.get_signature().is_array()

    def is_object(self): return self.getsignature().is_object()

    

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

from chj.index.JType import JavaTypesBase

class Classname(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_package_name(self):
        return '.'.join( [ str(self.tpd.get_string(int(x))) for x in self.args[:-1] ] )

    def get_abbreviated_package_name(self):
        return ''.join( [ str(self.tpd.get_string(int(x)))[0] for x in self.args[:-1] ])

    def get_qname(self):
        return self.get_package_name() + '.' + self.get_simple_name()

    def get_aqname(self):
        if len(self.args) > 0:
            return self.get_simple_name()
        else:
            return self.get_abbreviated_package_name() + '.' + self.get_simple_name() 
            
    def get_simple_name(self): return str(self.tpd.get_string(int(self.args[-1])))

    def get_name(self):
        if len(self.args) > 0:
            return self.get_package_name() + '.' + self.get_simple_name()
        else:
            return self.get_simple_name()

    def __str__(self): return self.get_name()

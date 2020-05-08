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

class MethodSignature(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)
        self.name = str(self.tpd.get_string(int(self.args[0])))
        self.descriptor = self.tpd.get_method_descriptor(int(self.args[1]))
        self.isstatic = int(self.args[2]) == 1

    def __str__(self): return self.name + ':' + str(self.descriptor)


class ClassMethodSignature(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)
        self.cnix = int(self.args[0])
        self.msix = int(self.args[1])
        self.classname = self.tpd.get_class_name(self.cnix)
        self.signature = self.tpd.get_method_signature_data(self.msix)
        self.methodname = self.signature.name

    def get_aqname(self):
        '''return fully qualified method name with abbreviated package name.'''
        return (self.classname.get_aqname() + '.' + str(self.methodname))

    def get_qname(self): return self.__str__()

    def get_signature(self): return str(self.signature)

    def __str__(self):
        return str(self.classname) + '.' + str(self.signature)

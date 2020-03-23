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


class Instruction(object):

    def __init__(self,jmethod,pc,opc,exprstack,tgts=None):
        self.jmethod = jmethod
        self.pc = pc
        self.opc = opc
        self.exprstack = exprstack
        self.tgts = tgts

    def has_targets(self): return not (self.tgts is None)

    def get_targets(self): return self.tgts.cnixs

    def get_cmsix_targets(self):
        isig = self.opc.get_signature()
        if self.has_targets():
            return [ self.jmethod.jd.get_cmsix(cnix,isig.index) for cnix in self.get_targets() ]
        else:
            return []

    def get_loop_depth(self):
        return self.jmethod.get_loop_depth(self.pc)

    def is_call(self): return self.opc.is_call()

    def is_load_string(self): return self.opc.is_load_string()

    def is_put_field(self): return self.opc.is_put_field()

    def is_put_static(self): return self.opc.is_put_static()

    def is_get_field(self): return self.opc.is_get_field()

    def is_get_static(self): return self.opc.is_get_static()

    def is_object_created(self): return self.opc.is_object_created()

    def get_string_constant(self): return self.opc.get_string_constant()

    def get_cn(self): return self.opc.get_cn()

    def get_signature(self): return self.opc.get_signature()

    def get_field(self): return self.opc.get_field()

    def __str__(self): return str(self.opc)

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


import chj.util.printutil as UP

class FinallyHandler(object):

    def __init__(self,jtable,xnode):
        self.jtable = jtable
        self.startpc = int(xnode.get('start'))
        self.endpc = int(xnode.get('end'))
        self.handlerpc = int(xnode.get('pc'))


class ExceptionHandler(FinallyHandler):

    def __init__(self,jtable,xnode):
        FinallyHandler.__init__(self,jtable,xnode)
        self.jd = jtable.jmethod.jd
        self.cnix = int(xnode.get('cnix'))

    def get_class_name(self): return self.jd.get_cn(self.cnix)


class ExceptionTable():

    def __init__(self,jmethod,xnode):
        self.jmethod = jmethod
        self.exceptionhandlers = []
        self.finallyhandlers = []
        self._initialize(xnode)

    def tostring(self):
        lines = []
        def p(pc): return str(pc).rjust(5)
        if self.exceptionhandlers:
            for h in self.exceptionhandlers:
                lines.append(p(h.startpc) + '  ' + p(h.endpc) + '  ' +
                             p(h.handlerpc) + '  ' + str(h.get_class_name()))
        if self.finallyhandlers:
            for h in self.finallyhandlers:
                lines.append(p(h.startpc) + '  ' + p(h.endpc) + '  ' +
                             p(h.handlerpc) + '  ' + 'finally')
        return '\n'.join(lines)

    def _initialize(self,xnode):
        xhandlers = xnode.findall('handler')
        if xhandlers is None: return
        for xh in xhandlers:
            if 'cnix' in xh.attrib:
                self.exceptionhandlers.append(ExceptionHandler(self,xh))
            else:
                self.finallyhandlers.append(FinallyHandler(self,xh))

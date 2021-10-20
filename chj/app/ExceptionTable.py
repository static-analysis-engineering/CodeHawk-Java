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
import chj.util.fileutil as UF

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from chj.app.JavaMethod import JavaMethod
    from chj.index.Classname import Classname

class FinallyHandler(object):

    def __init__(self, jtable: "ExceptionTable", xnode:"ET.Element"):
        self.jtable = jtable
        self.xnode = xnode

    @property
    def startpc(self) -> int:
        startpc = self.xnode.get('start')
        if startpc is not None:
            return int(startpc)
        else:
            raise UF.CHJError('startpc missing from xml for Exception')

    @property
    def endpc(self) -> int:
        endpc = self.xnode.get('end')
        if endpc is not None:
            return int(endpc)
        else:
            raise UF.CHJError('endpc missing from xml for Exception')

    @property
    def handlerpc(self) -> int:
        handlerpc = self.xnode.get('pc')
        if handlerpc is not None:
            return int(handlerpc)
        else:
            raise UF.CHJError('pc missing from xml for Exception')

class ExceptionHandler(FinallyHandler):

    def __init__(self, jtable: "ExceptionTable", xnode:"ET.Element"):
        FinallyHandler.__init__(self,jtable,xnode)
        self.jd = jtable.jmethod.jd
        self.xnode = xnode

    @property
    def cnix(self) -> int:
        cnix = self.xnode.get('cnix')
        if cnix is not None:
            return int(cnix)
        else:
            raise UF.CHJError('cnix missing from xml for Exception')

    def get_class_name(self) -> "Classname": return self.jd.get_cn(self.cnix)


class ExceptionTable():

    def __init__(self, jmethod: "JavaMethod", xnode: "ET.Element"):
        self.jmethod = jmethod
        self.exceptionhandlers: List[ExceptionHandler] = []
        self.finallyhandlers: List[FinallyHandler] = []
        self._initialize(xnode)

    def tostring(self) -> str:
        lines = []
        def p(pc: int) -> str: return str(pc).rjust(5)
        if self.exceptionhandlers:
            for h in self.exceptionhandlers:
                lines.append(p(h.startpc) + '  ' + p(h.endpc) + '  ' +
                             p(h.handlerpc) + '  ' + str(h.get_class_name()))
        if self.finallyhandlers:
            for j in self.finallyhandlers:
                lines.append(p(j.startpc) + '  ' + p(j.endpc) + '  ' +
                             p(j.handlerpc) + '  ' + 'finally')
        return '\n'.join(lines)

    def _initialize(self, xnode:"ET.Element") -> None:
        xhandlers = xnode.findall('handler')
        if xhandlers is None: return
        for xh in xhandlers:
            if 'cnix' in xh.attrib:
                self.exceptionhandlers.append(ExceptionHandler(self,xh))
            else:
                self.finallyhandlers.append(FinallyHandler(self,xh))

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

from typing import cast, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.app.JavaMethod import JavaMethod
    from chj.app.ExceptionTable import ExceptionTable

class ExceptionHandlers():

    def __init__(self, app: "AppAccess"):
        self.app = app

    def as_dictionary(self) -> Dict[int, List[ Tuple[int, int, int, str, str] ] ]:
        result = []
        table: Dict[int, List[Tuple[int, int, int, str, str]]] = {}
        def f(cmsix: int, m: "JavaMethod") -> None:
            if m.has_exception_table():
                result.append((cmsix,m.get_exception_table()))
        self.app.iter_methods(f)
        for (cmsix,t) in result:
            t = cast("ExceptionTable", t)       #guaranteed by has_exception_table check
            for ex in t.exceptionhandlers:
                aqname = str(self.app.jd.get_cms(cmsix).get_aqname())
                if not cmsix in table:
                    table[cmsix] = [ ( ex.startpc, ex.endpc, ex.handlerpc,
                                           ex.get_class_name().get_name(), aqname ) ]
                else:
                    table[cmsix].append( ( ex.startpc, ex.endpc, ex.handlerpc,
                                           ex.get_class_name().get_name(), aqname ) )
        return table

    def tostring(self) -> str:
        result = []
        lines = []
        def f(cmsix: int, m: "JavaMethod") -> None:
            if m.has_exception_table():
                result.append((cmsix,m.get_exception_table()))
        self.app.iter_methods(f)
        lines.append(' ')
        lines.append('start-pc  end-pc  handler-pc')
        for (cmsix,t) in result:
            t = cast("ExceptionTable", t)       #guaranteed by has_exception_table check
            lines.append(' ')
            lines.append(self.app.jd.get_cms(cmsix).get_aqname())
            lines.append(t.tostring())
        return '\n'.join(lines)

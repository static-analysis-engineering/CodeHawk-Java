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

from typing import Dict, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.app.JavaMethod import JavaMethod

import chj.util.printutil as UP

class BranchConditions():

    def __init__(self, app: "AppAccess"):
        self.app = app

    def get_table(self) -> Dict[str, List[Tuple[int, str]]]:
        result = []
        def f(cmsix: int, m: "JavaMethod") -> None:
            for c in m.get_conditions():
                result.append((cmsix, m.get_aqname(), c[0]))
        self.app.iter_methods(f)
        table: Dict[str, List[Tuple[int, str]]] = {}

        for (cmsix, name, cond) in result:
            if cond in table:
                table[cond].append( (cmsix, name) )
            else:
                table[cond] = [ (cmsix, name) ]

#        for (name, cond) in result:
#            if cond in table:
#                if isinstance(table[cond],int):
#                    table[cond] += 1
#                else:
#                    table[cond] = 2
#            else:
#                table[cond] = name

        return table
         
    def as_dictionary(self) -> Dict[str, List[Tuple[int, str]]]:
        table = self.get_table()
        return table

    def tostring(self) -> str:
        result = []
        def f(cmsix: int, m: "JavaMethod") -> None:
            for c in m.get_conditions():
                result.append((m.get_aqname(),c[0]))
        self.app.iter_methods(f)
        table: Dict[str, Union[str, int]] = {}
        for (name, cond) in result:
            if cond in table:
                if isinstance(table[cond], int):
                    table[cond] += 1
                else:
                    table[cond] = 2
            else:
                table[cond] = name
        if len(table) > 0:
            slen = max(len(s) for s in table) + 2
        if slen > 60: slen = 80
        else:
            slen = 50
        header = [ ('condition',len) ]
        headerline = ''.join([UP.cjust(str(t[0]),slen) for t in header]) + 'method name or occurrences'
        lines = []
        lines.append(headerline)
        lines.append('-' * 80)
        for (c,n) in sorted(table.items(),key = lambda x:x[0]):
            lines.append(c.ljust(slen) + '  ' + str(n))
        return '\n'.join(lines)

    def toincludestring(self, s: str) -> str:
        result = []
        def f(cmsix: int, m: "JavaMethod") -> None:
            for c in m.get_conditions():
                result.append((m.get_aqname(),c[0]))
        self.app.iter_methods(f)
        table: Dict[str, Union[str, int]] = {}
        for (name,cond) in result:
            if s in cond:
                if cond in table:
                    if isinstance(table[cond], int):
                        table[cond] += 1
                    else:
                        table[cond] = 2
                else:
                    table[cond] = name
        if len(table) > 0:
            slen = max(len(s) for s in table) + 2
            header = [ ('condition',len) ]
            headerline = ''.join([UP.cjust(str(t[0]),slen) for t in header]) + 'method name or occurrences'
            lines = []
            lines.append(headerline)
            lines.append('-' * 80)
            for (c,n) in sorted(table.items(), key = lambda x:x[0]):
                lines.append(c.ljust(slen) + str(n))
            return '\n'.join(lines)
        else:
            return('No matching conditions were found')


    

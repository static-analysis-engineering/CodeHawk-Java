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

import chj.util.printutil as UP

from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess

class BytecodeReport(object):

    def __init__(self, app: "AppAccess", cmsix: int):
        self.app = app
        self.jd = self.app.jd
        self.cmsix = cmsix

    def as_list(self) -> List[List[str]]:
        jmethod = self.app.get_method(self.cmsix)
        instrs = jmethod.instructions
        lines = []
        for pc in sorted(instrs):
            instr = instrs[pc]
            lines.append([str(pc), str(instr)])
        return lines

    def as_dictionary(self) -> Dict[str, str]:
        jmethod = self.app.get_method(self.cmsix)
        instrs = jmethod.instructions
        result = {}
        for pc in sorted(instrs):
            result[str(pc)] = str(instrs[pc])
        return result

    def to_string(self,showstack: bool=False, showtargets: bool=False, showinvariants: bool=False) -> str:
        jmethod = self.app.get_method(self.cmsix)
        instrs = jmethod.instructions
        lines = []
        lines.append(jmethod.get_qname())
        lines.append(str(jmethod.variabletable))
        for pc in sorted(instrs):
            instr = instrs[pc]
            lines.append(str(pc).rjust(4) + '  ' + str(instr))
            if showtargets and instr.has_targets():
                lines.append(' '.rjust(28)  + str(instr.tgts) +'\n')
            if showstack: lines.append(str(instr.exprstack) + '\n')
        if showinvariants:
            lines.append('\nInvariants per pc:')
            lines.append(str(jmethod.invariants))
        return '\n'.join(lines)

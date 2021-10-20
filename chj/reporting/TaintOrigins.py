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

from typing import Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.index.DataDictionary import DataDictionary

import chj.util.printutil as UP

import chj.index.Taint as T

TORIGIN_CONSTRUCTOR_TYPE = Union[T.VariableTaint,
                            T.FieldTaint,
                            T.CallerTaint,
                            T.TopTargetTaint,
                            T.StubTaint]

class TaintOrigins():

    def __init__(self,app: "AppAccess"):
        self.app = app
        self.jd: "DataDictionary" = app.jd

    def as_dictionary(self) -> Dict[str, str]:
        results = {}
        def f(origin: TORIGIN_CONSTRUCTOR_TYPE) -> None:
            results[str(origin.index)] = str(origin)
        self.jd.iter_taint_origins(f)
        return results

    def tostring(self, source: Optional[str]) -> str:
        header = [('index',8)]
        headerline = ''.join([UP.cjust(str(t[0]),8) for t in header]) + ' taint origin site'
        result = []
        lines= []
        def f(origin: TORIGIN_CONSTRUCTOR_TYPE) -> None:
            if source is None or source in str(origin):
                result.append(str(origin.index).rjust(6) + '  ' + str(origin))
        self.jd.iter_taint_origins(f)
        lines.append(headerline)
        lines.append('-' * 80)
        for t in sorted(result):
            lines.append(t)
        return '\n'.join(lines)

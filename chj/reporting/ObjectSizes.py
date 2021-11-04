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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaClass import JavaClass
    from chj.index.AppAccess import AppAccess

class ObjectSizes():

    def __init__(self, app: "AppAccess"):
        self.app = app
        self.jd = app.jd

    def to_string(self) -> str:
        result = []
        def f(c: "JavaClass") -> None: result.append((c,c.get_object_size()))
        self.app.iter_classes(f)

        lines = []
        for (c,objsize) in sorted(result,key=lambda x:x[1].scalar,reverse=True):
            lines.append(c.get_qname())
            lines.append(('  scalar size: ' + str(objsize.scalar)))
            objects = objsize.objects
            nArrays = len(objsize.arrays)
            if len(objects) > 0:
                pObjs = ', '.join([ str(x) for x in objects])
                lines.append('  objects    : ' + pObjs)
            if nArrays > 0:
                lines.append('  arrays     : ' + str(nArrays))
            lines.append(' ')
        return '\n'.join(lines)
                             

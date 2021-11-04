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

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaClass import JavaClass
    from chj.index.FieldSignature import FieldSignature
    from chj.index.FieldSignature import ClassFieldSignature

class ObjectSize(object):

    def __init__(self, jclass: "JavaClass"):
        self.jclass = jclass                        # JavaClass
        self.jd = jclass.jd                         # DataDictionary
        self.scalar = 0
        self.objects: List[int] = []                # [ cnix ]
        self.arrays: List["FieldSignature"] = []    # [ FieldSignature ]

    def add_scalar(self, s: int) -> None:
        self.scalar += s

    def add_object(self, cnix: int) -> None:
        self.objects.append(cnix)

    def add_array(self, arr: "FieldSignature") -> None:
        self.arrays.append(arr)

    def add_field(self, fsig: "FieldSignature") -> None:
        self.add_scalar(fsig.get_scalar_size())
        if fsig.is_object(): self.add_object(fsig.get_object_type())
        if fsig.is_array(): self.add_array(fsig)

    def add_object_size(self, other: "ObjectSize") -> None:
        self.scalar += other.scalar
        self.objects.extend(other.objects)
        self.arrays.extend(other.arrays)

    def to_string(self) -> str:
        lines = []
        lines.append('  scalar size: ' + str(self.scalar))
        if len(self.objects) > 0:
            pObjs = '. '.join([self.jd.get_cn(cnix).get_name() for cnix in self.objects])
            lines.append('  objects    : ' + pObjs)
        if len(self.arrays) > 0:
            lines.append('  arrays     : ' + str(len(self.arrays)))
        return '\n'.join(lines)

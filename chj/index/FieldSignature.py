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

from chj.index.JType import JavaTypesBase

from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.Classname import Classname
    from chj.index.JTypeDictionary import JTypeDictionary

class FieldSignature(JavaTypesBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_type(self) -> Any: return self.tpd.get_value_type(int(self.args[1]))

    def get_name(self) -> str: return str(self.tpd.get_string(self.args[0]))

    def get_scalar_size(self) -> int: return self.get_type().get_scalar_size()

    def get_object_type(self) -> Any:
        if self.is_object():
            return self.get_type().get_object_type()

    def is_scalar(self) -> bool: return self.get_type().is_scalar()

    def is_array(self) -> bool: return self.get_type().is_array()

    def is_object(self) -> bool: return self.get_type().is_object()

    def __str__(self) -> str: return self.get_name()


class ClassFieldSignature(JavaTypesBase):

    def __init__(self,
        tpd: "JTypeDictionary",
        index: int,
        tags: List[str],
        args: List[int]):
        JavaTypesBase.__init__(self,tpd,index,tags,args)
        self.cnix = int(self.args[0])
        self.fsix = int(self.args[1])

    def get_signature(self) -> "FieldSignature":
        return self.tpd.get_field_signature_data(self.fsix)

    def get_class_name(self) -> "Classname":
        return self.tpd.get_class_name(self.cnix)

    def __str__(self) -> str:
        return str(self.get_class_name()) + '.' + str(self.get_signature())

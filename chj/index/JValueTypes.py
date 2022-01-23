# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Andrew McGraw
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
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

import chj.index.JDictionaryRecord as JD
import chj.util.fileutil as UF

from typing import List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.JTypeDictionary import JTypeDictionary
    from chj.index.JObjectTypes import JObjectTypeBase
    from chj.index.Classname import Classname

class JValueTypeBase(JD.JDictionaryRecord):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,tpd,index,tags,args)

    def is_object_value_type(self) -> bool: return False

    def is_object_type(self) -> bool: return False

    def is_object(self) -> bool: return False

    def is_array_type(self) -> bool: return False

    def is_basic_type(self) -> bool: return False

    def is_scalar(self) -> bool: return False

    def is_scalara(self) -> bool: return False

    def is_long(self) -> bool: return False

    def is_double(self) -> bool: return False

    def get_scalar_size(self) -> int: return 4

    def __str__(self) -> str: return 'jvaluetypebase'

@JD.j_dictionary_record_tag("o")
class ObjectValueType(JValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JValueTypeBase.__init__(self,tpd,index,tags,args)

    def is_object_value_type(self) -> bool: return True

    def is_object_type(self) -> bool: return True

    def is_object(self) -> bool: return True

    def is_array_type(self) -> bool: return self.get_object_type().is_object_array_type()

    def get_object_type(self) -> "JObjectTypeBase": return self.tpd.get_object_type(int(self.args[0]))

    def get_class(self) -> "Classname":
        if self.is_object():
            return self.get_object_type().get_class()
        else:
            raise UF.CHJError(str(self) + " is not an objecttype")

    def __str__(self) -> str: return str(self.get_object_type())

@JD.j_dictionary_record_tag("b")
class BasicValueType(JValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JValueTypeBase.__init__(self,tpd,index,tags,args)

    def get_scalar_size(self) -> int:
        if self.is_long() or self.is_double():
            return 8
        else:
            return 4

    def is_basic_type(self) -> bool: return True

    def is_scalara(self) -> bool: return True

    def is_long(self) -> bool: return self.tags[1] == 'L'

    def is_double(self) -> bool: return self.tags[1] == 'D'

    def get_basic_type(self) -> str: return self.tags[1]

    def __str__(self) -> str: return str(self.get_basic_type())

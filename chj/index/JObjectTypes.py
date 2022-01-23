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

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.JTypeDictionary import JTypeDictionary
    from chj.index.Classname import Classname
    from chj.index.JValueTypes import JValueTypeBase

class JObjectTypeBase(JD.JDictionaryRecord):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,tpd,index,tags,args)

    def is_object_array_type(self) -> bool:
        return False

    def is_array(self) -> bool:
        return False

    def is_object_value_type(self) -> bool:
        return False

    def is_object_type(self) -> bool:
        return False

    def is_object(self) -> bool:
        return False

    def get_class(self) -> "Classname":
        raise NotImplementedError('get_class not implemented for JObjectTypeBase')

    def __str__(self) -> str:
        return 'jobjecttypebase'

@JD.j_dictionary_record_tag("c")
class ClassObjectType(JObjectTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JObjectTypeBase.__init__(self,tpd,index,tags,args)

    def get_class(self) -> "Classname": return self.tpd.jd.get_cn(int(self.args[0]))

    def is_object(self) -> bool: return True

    def __str__(self) -> str: return str(self.get_class())

@JD.j_dictionary_record_tag("a")
class ArrayObjectType(JObjectTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JObjectTypeBase.__init__(self,tpd,index,tags,args)

    def is_object_array_type(self) -> bool: return True

    def is_array(self) -> bool: return True

    def get_value_type(self) -> "JValueTypeBase": return self.tpd.get_value_type(int(self.args[0]))

    def __str__(self) -> str: return str(self.get_value_type())

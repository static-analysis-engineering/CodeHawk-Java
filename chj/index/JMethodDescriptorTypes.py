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
from chj.index.JValueTypes import JValueTypeBase
import chj.util.fileutil as UF

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.JTypeDictionary import JTypeDictionary

class JMethodDescriptorTypeBase(JD.JDictionaryRecord):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,tpd,index,tags,args)

    def __str__(self) -> str:
        return 'jmethodescriptortypebase'

@JD.j_dictionary_record_tag("m")
class MethodDescriptor(JMethodDescriptorTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JMethodDescriptorTypeBase.__init__(self,tpd,index,tags,args)

    def has_return_value(self) -> bool: return int(self.args[0]) == 1

    def get_return_type(self) -> Optional[JValueTypeBase]:
        if self.has_return_value():
            return self.tpd.get_value_type(int(self.args[1]))
        else:
            return None

    def get_argument_types(self) -> List[JValueTypeBase]:
        if self.has_return_value():
            return [ self.tpd.get_value_type(int(x)) for x in self.args[2:] ]
        else:
            return [ self.tpd.get_value_type(int(x)) for x in self.args[1:] ]

    def __str__(self) -> str:
        sreturn = '' if self.get_return_type() is None else str(self.get_return_type())
        return ('(' + ','.join([ str(x) for x in self.get_argument_types()])
                    + ')' + sreturn )

@JD.j_dictionary_record_tag("v")
class ValueDescriptor(JMethodDescriptorTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JMethodDescriptorTypeBase.__init__(self,tpd,index,tags,args)

    def get_value_type(self) -> JValueTypeBase: return self.tpd.get_value_type(int(self.args[0]))

    def __str__(self) -> str: return 'descr:' + str(self.get_value_type())

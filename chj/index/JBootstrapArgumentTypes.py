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
    from chj.index.JConstValueTypes import JConstValueTypeBase
    from chj.index.JMethodHandleTypes import JMethodHandleTypeBase
    from chj.index.JMethodDescriptorTypes import MethodDescriptor

class JBootstrapArgumentTypeBase(JD.JDictionaryRecord):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,tpd,index,tags,args)

    def __str__(self) -> str:
        return 'jboostrapargumenttypebase'

@JD.j_dictionary_record_tag("c")
class BootstrapArgConstantValue(JBootstrapArgumentTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JBootstrapArgumentTypeBase.__init__(self,tpd,index,tags,args)

    def get_constant_value(self) -> "JConstValueTypeBase":
        return self.tpd.get_constant_value(int(self.args[0]))

    def __str__(self) -> str: return str(self.get_constant_value())

@JD.j_dictionary_record_tag("h")
class BootstrapArgMethodHandle(JBootstrapArgumentTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JBootstrapArgumentTypeBase.__init__(self,tpd,index,tags,args)

    def get_reference_kind(self) -> str: return self.tags[1]

    def get_method_handle_type(self) -> "JMethodHandleTypeBase":
        return self.tpd.get_method_handle_type(int(self.args[0]))

    def __str__(self) -> str:
        return (str(self.get_method_handle_type())
                    + '(' + self.get_reference_kind() + ')')

@JD.j_dictionary_record_tag("t")
class BootstrapArgMethodType(JBootstrapArgumentTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JBootstrapArgumentTypeBase.__init__(self,tpd,index,tags,args)

    def get_method_descriptor(self) -> "MethodDescriptor":
        return self.tpd.get_method_descriptor(int(self.args[0]))

    def __str__(self) -> str: return str(self.get_method_descriptor())

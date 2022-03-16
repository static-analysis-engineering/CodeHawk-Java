# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2019 Kestrel Technology LLC
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

from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.Classname import Classname
    from chj.index.JTypeDictionary import JTypeDictionary
    from chj.index.JMethodHandleTypes import JMethodHandleTypeBase
    from chj.index.JBootstrapArgumentTypes import JBootstrapArgumentTypeBase

class JavaTypesBase(JD.JDictionaryRecord):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,tpd,index,tags,args)
        self.tpd = tpd

    def get_scalar_size(self) -> int: return 4

    def is_scalar(self) -> bool: return False

    def is_array(self) -> bool: return False

    def is_object(self) -> bool: return False

    def __str__(self) -> str: return 'javatypesbase'

class StringConstant(JavaTypesBase):
    
    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_string(self) -> str:
        if len(self.tags) > 0:
            return self.tags[0]
        else:
            return ''

    def get_string_length(self) -> int: return int(self.args[0])

    def is_hex(self) -> bool: return len(self.tags) > 1

    def __str__(self) -> str:
        if self.is_hex():
            return ('(' + str(self.get_string_length()) + '-char-string' +')')
        else:
            return self.get_string()

class BootstrapMethodData(JavaTypesBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_reference_kind(self) -> str: return self.tags[1]

    def get_method_handle_type(self) -> "JMethodHandleTypeBase":
        return self.tpd.get_method_handle_type(int(self.args[0]))

    def get_arguments(self) -> List["JBootstrapArgumentTypeBase"]:
        return [ self.tpd.get_bootstrap_argument(int(x)) for x in self.args[1:] ]

    def __str__(self) -> str:
        return (str(self.get_method_handle_type()) + '('
                    + ','.join([ str(x) for x in self.get_arguments() ]) + ')')

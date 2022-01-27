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
    from chj.index.JType import StringConstant
    from chj.index.JTypeDictionary import JTypeDictionary
    from chj.index.JObjectTypes import JObjectTypeBase

class JConstValueTypeBase(JD.JDictionaryRecord):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,tpd,index,tags,args)

    def __str__(self) -> str: return 'jconstvaluetypebase'

@JD.j_dictionary_record_tag("s")
class ConstString(JConstValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstValueTypeBase.__init__(self,tpd,index,tags,args)

    def get_string(self) -> "StringConstant": return self.tpd.get_string(int(self.args[0]))

    def __str__(self) -> str: return str(self.get_string())

@JD.j_dictionary_record_tag("i")
class ConstInt(JConstValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstValueTypeBase.__init__(self,tpd,index,tags,args)

    def get_int(self) -> int: return int(self.args[0])

    def __str__(self) -> str: return str(self.get_int())

@JD.j_dictionary_record_tag("f")
class ConstFloat(JConstValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstValueTypeBase.__init__(self,tpd,index,tags,args)

    def get_float(self) -> float: return float(self.tags[1])

    def __str__(self) -> str: return self.tags[1]

@JD.j_dictionary_record_tag("l")
class ConstLong(JConstValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstValueTypeBase.__init__(self,tpd,index,tags,args)

    def get_long(self) -> int: return int(self.tags[1])

    def __str__(self) -> str: return self.tags[1]

@JD.j_dictionary_record_tag("d")
class ConstDouble(JConstValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstValueTypeBase.__init__(self,tpd,index,tags,args)

    def get_double(self) -> float: return float(self.tags[1])

    def __str__(self) -> str: return self.tags[1]

@JD.j_dictionary_record_tag("c")
class ConstClass(JConstValueTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstValueTypeBase.__init__(self,tpd,index,tags,args)

    def get_class(self) -> "JObjectTypeBase":
        return self.tpd.get_object_type(int(self.args[0]))

    def __str__(self) -> str: return str(self.get_class())
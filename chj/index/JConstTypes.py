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
    from chj.index.Classname import Classname
    from chj.index.FieldSignature import FieldSignature
    from chj.index.MethodSignature import MethodSignature
    from chj.index.JTypeDictionary import JTypeDictionary
    from chj.index.JObjectTypes import JObjectTypeBase
    from chj.index.JType import StringConstant
    from chj.index.JMethodDescriptorTypes import JMethodDescriptorTypeBase
    from chj.index.JMethodHandleTypes import JMethodHandleTypeBase
    from chj.index.JConstValueTypes import JConstValueTypeBase

class JConstTypeBase(JD.JDictionaryRecord):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,tpd,index,tags,args)

    def __str__(self) -> str:
        return 'jconsttypebase'

@JD.j_dictionary_record_tag("v")
class ConstValue(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_constant_value(self) -> "JConstValueTypeBase":
        return self.tpd.get_constant_value(self.args[0])

    def __str__(self) -> str: return 'C:' + str(self.get_constant_value())

@JD.j_dictionary_record_tag("f")
class ConstField(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_class_name(self) -> "Classname":
        return self.tpd.jd.get_cn(int(self.args[0]))

    def get_field_signature(self) -> "FieldSignature":
        return self.tpd.jd.get_fs(int(self.args[1]))

    def __str__(self) -> str:
        return 'C:' + str(self.get_class_name()) + '.' + str(self.get_field_signature())

@JD.j_dictionary_record_tag("m")
class ConstMethod(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_object_type(self) -> "JObjectTypeBase":
        return self.tpd.get_object_type(int(self.args[0]))

    def get_method_signature(self) -> "MethodSignature":
        return self.tpd.jd.get_ms(int(self.args[1]))

    def __str__(self) -> str:
        return 'C:' + str(self.get_object_type()) + '.' + str(self.get_method_signature())

@JD.j_dictionary_record_tag("i")
class ConstInterfaceMethod(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_class_name(self) -> "Classname":
        return self.tpd.jd.get_cn(int(self.args[0]))

    def get_method_signature(self) -> "MethodSignature":
        return self.tpd.jd.get_ms(int(self.args[1]))

    def __str__(self) -> str:
        return 'C:' + str(self.get_class_name()) + '.' + str(self.get_method_signature())


@JD.j_dictionary_record_tag("d")
class ConstDynamicMethod(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_bootstrap_method_index(self) -> int:
        return int(self.args[0])

    def get_method_signature(self) -> "MethodSignature":
        return self.tpd.jd.get_ms(int(self.args[1]))

    def __str__(self) -> str:
        return ('C:Dynamic(' + str(self.get_bootstrap_method_index()) + ').'
                    + str(self.get_method_signature()))

@JD.j_dictionary_record_tag("n")
class ConstNameAndType(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_name(self) -> "StringConstant":
        return self.tpd.get_string(int(self.args[0]))

    def get_type(self) -> "JMethodDescriptorTypeBase":
        return self.tpd.get_descriptor(int(self.args[1]))

    def __str__(self) -> str: return 'CNT:' + str(self.get_name()) + ':' + str(self.get_type())

@JD.j_dictionary_record_tag("s")
class ConstStringUTF8(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_string(self) -> "StringConstant":
        return self.tpd.get_string(int(self.args[0]))

    def __str__(self) -> str: return 'C:' + str(self.get_string())

@JD.j_dictionary_record_tag("h")
class ConstMethodHandle(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_reference_kind(self) -> str: return self.tags[1]

    def get_method_handle_type(self) -> "JMethodHandleTypeBase":
        return self.tpd.get_method_handle_type(int(self.args[0]))

    def __str__(self) -> str:
        return ('C:' + str(self.get_method_handle_type())
                    + '(' + self.get_reference_kind() + ')')

@JD.j_dictionary_record_tag("t")
class ConstMethodType(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def get_method_descriptor(self) -> "JMethodDescriptorTypeBase":
        return self.tpd.get_method_descriptor(int(self.args[0]))

    def __str__(self) -> str:
        return 'C:' + str(self.get_method_descriptor())

@JD.j_dictionary_record_tag("u")
class ConstUnusable(JConstTypeBase):

    def __init__(self,
            tpd: "JTypeDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JConstTypeBase.__init__(self,tpd,index,tags,args)

    def __str__(self) -> str: return 'unusable'

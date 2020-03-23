# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2019 Kestrel Technology LLC
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

class JavaTypesBase(JD.JDictionaryRecord):

    def __init__(self,tpd,index,tags,args):
        JD.JDictionaryRecord.__init__(self,index,tags,args)
        self.tpd = tpd

    def get_scalar_size(self): return 4

    def is_scalar(self): return False

    def is_array(self): return False

    def is_object(self): return False

    def __str__(self): return 'javatypesbase'


class StringConstant(JavaTypesBase):
    
    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_string(self):
        if len(self.tags) > 0:
            return self.tags[0]
        else:
            return ''

    def get_string_length(self): return int(self.args[0])

    def is_hex(self): return len(self.tags) > 1

    def __str__(self):
        if self.is_hex():
            return ('(' + str(self.get_string_length()) + '-char-string' +')')
        else:
            return self.get_string()


class ClassObjectType(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_class(self): return self.tpd.jd.get_cn(int(self.args[0]))

    def is_object(self): return True

    def __str__(self): return str(self.get_class())


class ArrayObjectType(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def is_object_array_type(self): return True

    def is_array(self): return True

    def get_value_type(self): return self.tpd.get_value_type(int(self.args[0]))

    def __str__(self): return str(self.get_value_type())

        
class ObjectValueType(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def is_object_value_type(self): return True

    def is_object_type(self): return True

    def is_object(self): return True

    def is_array_type(self): return self.get_object_type().is_object_array_type()

    def get_object_type(self): return self.tpd.get_object_type(int(self.args[0]))

    def get_class(self): return self.get_object_type().get_class()

    def __str__(self): return str(self.get_object_type())


class BasicValueType(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_scalar_size(self):
        if self.is_long() or self.is_double():
            return 8
        else:
            return 4

    def is_basic_type(self): return True

    def is_scalara(self): return True

    def is_long(self): return self.tags[1] == 'L'

    def is_double(self): return self.tags[1] == 'D'

    def get_basic_type(self): return self.tags[1]

    def __str__(self): return str(self.get_basic_type())


class MethodDescriptor(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def has_return_value(self): return int(self.args[0]) == 1

    def get_return_type(self):
        if self.has_return_value():
            return self.tpd.get_value_type(int(self.args[1]))

    def get_argument_types(self):
        if self.has_return_value():
            return [ self.tpd.get_value_type(int(x)) for x in self.args[2:] ]
        else:
            return [ self.tpd.get_value_type(int(x)) for x in self.args[1:] ]

    def __str__(self):
        sreturn = '' if self.get_return_type() is None else str(self.get_return_type())
        return ('(' + ','.join([ str(x) for x in self.get_argument_types()])
                    + ')' + sreturn )


class ValueDescriptor(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_value_type(self): return self.tpd.get_value_type(int(self.args[0]))

    def __str__(self): return 'descr:' + str(self.get_value_type())


class ConstString(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_string(self): return self.tpd.get_string(int(self.args[0]))

    def __str__(self): return self.get_string()


class ConstInt(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_int(self): return int(self.args[0])

    def __str__(self): return str(self.get_int())


class ConstFloat(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_float(self): return float(self.tags[1])

    def __str__(self): return self.tags[1]


def ConstLong(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_long(self): return int(self.tags[1])

    def __str__(self): return self.tags[1]


class ConstDouble(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_double(self): return float(tags[1])

    def __str__(self): return tags[1]


class ConstClass(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_class(self):
        return self.tpd.get_object_type(int(self.args[0]))

    def __str__(self): return str(self.get_class())


class FieldHandle(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_class_name(self):
        return self.tpd.jd.get_class(int(self.args[0]))

    def get_field_signature(self):
        return self.tpd.jd.get_field_signature(int(self.args[1]))

    def __str__(self):
        return str(self.get_class_name()) + ':' + str(self.get_field_signature())


class MethodHandle(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_object_type(self):
        return self.tpd.get_object_type(int(self.args[0]))

    def get_method_signature(self):
        return self.tpd.jd.get_method_signature(int(self.args[1]))

    def __str__(self):
        return str(self.get_object_type()) + ':' + str(self.get_method_signature())


class InterfaceHandle(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_class_name(self):
        return self.tpd.jd.get_class(int(self.args[0]))

    def get_method_signature(self):
        return self.tpd.jd.get_method+signature(int(self.args[1]))

    def __str__(self):
        return str(self.get_class_name()) + ':' + str(self.get_method_signature())


class ConstValue(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_constant_value(self):
        return self.jd.get_constant_value(self.args[0])

    def __str__(self): return 'C:' + str(self.get_constant_value())


class ConstField(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_class_name(self):
        return self.tpd.jd.get_cn(int(self.args[0]))

    def get_field_signature(self):
        return self.tpd.jd.get_field_signature(int(self.args[1]))

    def __str__(self):
        return 'C:' + str(self.get_class_name()) + '.' + str(self.get_field_signature())


class ConstMethod(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_object_type(self):
        return self.tpd.get_object_type(int(args[0]))

    def get_method_signature(self):
        return self.tpd.jd.get_method_signature(int(args[1]))

    def __str__(self):
        return 'C:' + str(self.get_object_type()) + '.' + str(self.get_method_signature())


class ConstInterfaceMethod(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_class_name(self):
        return self.tpd.jd.get_cn(int(self.args[0]))

    def get_method_signature(self):
        return self.tpd.jd.get_method_signature(int(self.args[1]))

    def __str__(self):
        return 'C:' + str(self.get_class_name()) + '.' + str(self.get_method_signature())


class ConstDynamicMethod(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_bootstrap_method_index(self):
        return int(self.args[0])

    def get_method_signature(self):
        return self.tpd.jd.get_method_signature(int(self.args[1]))

    def __str__(self):
        return ('C:Dynamic(' + str(self.get_bootstrap_mehtod_index()) + ').'
                    + str(self.get_method_signature()))


class ConstNameAndType(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_name(self):
        return self.tpd.get_string(int(self.args[0]))

    def get_type(self):
        return self.tpd.get_descriptor(int(self.args[1]))

    def __str__(self): return 'CNT:' + self.get_name() + ':' + str(self.get_type())


class ConstStringUTF8(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_string(self):
        return self.tpd.get_string(int(args[0]))

    def __str__(self): return 'C:' + self.get_string()


class ConstMethodHandle(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_reference_kind(self): return self.tags[1]

    def get_method_handle_type(self):
        return self.tpd.get_method_handle_type(int(self.args[0]))

    def __str__(self):
        return ('C:' + str(self.get_method_handle_type())
                    + '(' + self.get_reference_kind() + ')')


class ConstMethodType(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_method_descriptor(self):
        return self.tpd.get_method_descriptor(int(self.args[0]))

    def __str__(self):
        return 'C:' + str(self.get_method_descriptor())


class ConstUnusable(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def __str__(self): return 'unusable'


class BootstrapArgConstantValue(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_constant_value(self):
        return self.tpd.get_constant_value(int(self.args[0]))

    def __str__(self): return str(self.get_constant_value())


class BootstrapArgMethodHandle(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_reference_kind(self): return self.tags[1]

    def get_method_handle_type(self):
        return self.jd.get_method_handle_type(int(self.args[0]))

    def __str__(self):
        return (str(self.get_method_handle_type())
                    + '(' + self.get_reference_kind() + ')')


class BootstrapArgMethodType(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_method_descriptor(self):
        return self.tpd.get_method_descriptor(int(self.args[0]))

    def __str__(self): return str(self.get_method_descriptor())


class BootstrapMethodData(JavaTypesBase):

    def __init__(self,tpd,index,tags,args):
        JavaTypesBase.__init__(self,tpd,index,tags,args)

    def get_reference_kind(self): return self.tags[1]

    def get_method_handle_type(self):
        return self.tpd.get_method_handle_type(int(self.args[0]))

    def get_arguments(self):
        return [ self.tpd.get_bootstrap_argument(int(x)) for x in self.args[1:] ]

    def __str__(self):
        return (str(self.get_method_handle_types()) + '('
                    + ','.join([ str(x) for x in self.get_arguments() ]) + ')')

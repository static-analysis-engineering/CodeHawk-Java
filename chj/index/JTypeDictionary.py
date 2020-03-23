# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2020 Kestrel Technology LLC
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

import chj.util.IndexedTable as IT

import chj.index.JType as JT

from chj.index.Classname import Classname
from chj.index.FieldSignature import FieldSignature
from chj.index.MethodSignature import MethodSignature
from chj.index.FieldSignature import ClassFieldSignature
from chj.index.MethodSignature import ClassMethodSignature

object_type_constructors = {
    'c': lambda x:JT.ClassObjectType(*x),
    'a': lambda x:JT.ArrayObjectType(*x)
    }

value_type_constructors = {
    'o': lambda x:JT.ObjectValueType(*x),
    'b': lambda x:JT.BasicValueType(*x)
    }

descriptor_constructors = {
    'v': lambda x:JT.ValueDescriptor(*x),
    'm': lambda x:JT.MethodDescriptor(*x)
    }

constant_value_constructors = {
    's': lambda x:JT.ConstString(*x),
    'i': lambda x:JT.ConstInt(*x),
    'f': lambda x:JT.ConstFloat(*x),
    'l': lambda x:JT.ConstLong(*x),
    'd': lambda x:JT.ConstDouble(*x),
    'c': lambda x:JT.ConstClass(*x)
    }

method_handle_type_constructors = {
    'f': lambda x:JT.FieldHand(*x),
    'm': lambda x:JT.MethodHandle(*x),
    'i': lambda x:JT.InterfaceHandle(*x)
    }

constant_constructors = {
    'v': lambda x:JT.ConstValue(*x),
    'f': lambda x:JT.ConstField(*x),
    'm': lambda x:JT.ConstMethod(*x),
    'i': lambda x:JT.ConstInterfaceMethod(*x),
    'd': lambda x:JT.ConstDynamicMethod(*x),
    'n': lambda x:JT.ConstNameAndType(*xs),
    's': lambda x:JT.ConstStringUTF8(*x),
    'h': lambda x:JT.ConstMethodHandle(*x),
    't': lambda x:JT.ConstMethodType(*x),
    'u': lambda x:JT.ConstUnusable(*x)
    }

bootstrap_argument_constructors = {
    'c': lambda x:JT.BootstrapArgConstantValue(*x),
    'h': lambda x:JT.BootstrapArgMethodHandle(*x),
    't': lambda x:JT.BootstrapArgMethodType(*x)
    }

class JTypeDictionary(object):

    def __init__(self,jd,xnode):
        self.jd = jd
        self.string_table = IT.IndexedTable('string-table')
        self.class_name_table = IT.IndexedTable('class-name-table')
        self.object_type_table = IT.IndexedTable('object-type-table')
        self.value_type_table = IT.IndexedTable('value-type-table')
        self.method_descriptor_table = IT.IndexedTable('method-descriptor-table')
        self.descriptor_table = IT.IndexedTable('descriptor-table')
        self.field_signature_data_table = IT.IndexedTable('field-signature-data-table')
        self.method_signature_data_table = IT.IndexedTable('method-signature-data-table')
        self.class_field_signature_data_table = IT.IndexedTable('class-field-signature-data-table')
        self.class_method_signature_data_table = IT.IndexedTable('class-method-signature-data-table')
        self.constant_value_table = IT.IndexedTable('constant-value-table')
        self.method_handle_type_table = IT.IndexedTable('method-handle-type-table')
        self.constant_table = IT.IndexedTable('constant-table')
        self.bootstrap_argument_table = IT.IndexedTable('bootstrap-argument-table')
        self.bootstrap_method_data_table = IT.IndexedTable('bootstrap-method-data-table')
        self.tables = [
            (self.string_table, self._read_xml_string_table),
            (self.class_name_table, self._read_xml_class_name_table),
            (self.object_type_table, self._read_xml_object_type_table),
            (self.value_type_table, self._read_xml_value_type_table),
            (self.method_descriptor_table, self._read_xml_method_descriptor_table),
            (self.descriptor_table, self._read_xml_descriptor_table),
            (self.field_signature_data_table, self._read_xml_field_signature_data_table),
            (self.method_signature_data_table, self._read_xml_method_signature_data_table),
            (self.class_field_signature_data_table, self._read_xml_class_field_signature_data_table),
            (self.class_method_signature_data_table, self._read_xml_class_method_signature_data_table),
            (self.constant_value_table, self._read_xml_constant_value_table),
            (self.method_handle_type_table, self._read_xml_method_handle_type_table),
            (self.constant_table, self._read_xml_constant_table),
            (self.bootstrap_argument_table,self._read_xml_bootstrap_argument_table),
            (self.bootstrap_method_data_table, self._read_xml_bootstrap_method_data_table) ]
        self.initialize(xnode)

    def get_fields(self):
        return self.class_field_signature_data_table.indextable.values()

    def get_methods(self):
        return self.class_method_signature_data_table.indextable.values()

    def get_string(self,ix): return self.string_table.retrieve(ix)

    def get_class_name(self,ix): return self.class_name_table.retrieve(ix)

    def get_field_signature_data(self,ix): return self.field_signature_data_table.retrieve(ix)

    def get_class_field_signature_data(self,ix):
        return self.class_field_signature_data_table.retrieve(ix)

    def get_method_signature_data(self,ix):
        return self.method_signature_data_table.retrieve(ix)

    def get_class_method_signature_data(self,ix):
        return self.class_method_signature_data_table.retrieve(ix)

    def get_cms_index(self,tags,args):
        key = IT.get_key(tags,args)
        if self.class_method_signature_data_table.has_key(key):
            return self.class_method_signature_data_table.get_index(key)

    def get_object_type(self,ix): return self.object_type_table.retrieve(ix)

    def get_value_type(self,ix): return self.value_type_table.retrieve(ix)

    def get_method_descriptor(self,ix): return self.method_descriptor_table.retrieve(ix)

    def get_descriptor(self,ix): return self.descriptor_table.retrieve(ix)

    def get_method_handle_type(self,ix): return self.method_handle_type_table.retrieve(ix)

    def write_xml(self,node):
        def f(n,r):r.write_xml(n)
        for (t,_) in self.tables:
            tnode = ET.Element(t.name)
            t.write_xml(tnode,f)
            node.append(tnode)

    def __str__(self):
        lines = []
        for (t,_) in self.tables:
            if t.size() > 0:
                lines.append(str(t))
        return '\n'.join(lines)

    # ----------------------- Initialize dictionary from file ------------------
 
    def initialize(self,xnode,force=False):
        if xnode is None: return
        for (t,f) in self.tables:
            t.reset()
            f(xnode.find(t.name))
           
    def _read_xml_string_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.StringConstant(*args)
        self.string_table.read_xml(txnode,'n',get_value)

    def _read_xml_class_name_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return Classname(*args)
        self.class_name_table.read_xml(txnode,'n',get_value)

    def _read_xml_object_type_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return object_type_constructors[tag](args)
        self.object_type_table.read_xml(txnode,'n',get_value)

    def _read_xml_value_type_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return value_type_constructors[tag](args)
        self.value_type_table.read_xml(txnode,'n',get_value)

    def _read_xml_method_descriptor_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.MethodDescriptor(*args)
        self.method_descriptor_table.read_xml(txnode,'n',get_value)

    def _read_xml_field_signature_data_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return FieldSignature(*args)
        self.field_signature_data_table.read_xml(txnode,'n',get_value)

    def _read_xml_class_field_signature_data_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return ClassFieldSignature(*args)
        self.class_field_signature_data_table.read_xml(txnode,'n',get_value)

    def _read_xml_method_signature_data_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return MethodSignature(*args)
        self.method_signature_data_table.read_xml(txnode,'n',get_value)

    def _read_xml_class_method_signature_data_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return ClassMethodSignature(*args)
        self.class_method_signature_data_table.read_xml(txnode,'n',get_value)            

    def _read_xml_descriptor_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return descriptor_constructors[tag](args)
        self.descriptor_table.read_xml(txnode,'n',get_value)

    def _read_xml_constant_value_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return constant_value_constructors[tag](args)
        self.constant_value_table.read_xml(txnode,'n',get_value)

    def _read_xml_method_handle_type_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return method_handle_type_constructors[tag](args)
        self.method_handle_type_table.read_xml(txnode,'n',get_value)

    def _read_xml_constant_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return constant_constructors[tag](args)
        self.constant_table.read_xml(txnode,'n',get_value)

    def _read_xml_bootstrap_argument_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return bootstrap_argument_constructors[tag](args)
        self.bootstrap_argument_table.read_xml(txnode,'n',get_value)

    def _read_xml_bootstrap_method_data_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.BootstrapMethodData(*args)
        self.bootstrap_method_data_table.read_xml(txnode,'n',get_value)
        

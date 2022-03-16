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

import chj.index.JType as JT
import chj.index.JDictionaryRecord as JD

import chj.util.fileutil as UF
import chj.util.IndexedTable as IT
from chj.util.IndexedTable import (
    IndexedTable,
    IndexedTableValue,
    IndexedTableSuperclass
)

from chj.index.Classname import Classname
from chj.index.FieldSignature import FieldSignature
from chj.index.MethodSignature import MethodSignature
from chj.index.FieldSignature import ClassFieldSignature
from chj.index.MethodSignature import ClassMethodSignature

from chj.index.JObjectTypes import (
    JObjectTypeBase,
    ClassObjectType,
    ArrayObjectType,
)

from chj.index.JMethodHandleTypes import JMethodHandleTypeBase
from chj.index.JConstTypes import JConstTypeBase
from chj.index.JConstValueTypes import JConstValueTypeBase
from chj.index.JValueTypes import JValueTypeBase
from chj.index.JMethodDescriptorTypes import (
    JMethodDescriptorTypeBase,
    MethodDescriptor
)
from chj.index.JConstValueTypes import JConstValueTypeBase
from chj.index.JBootstrapArgumentTypes import JBootstrapArgumentTypeBase

import xml.etree.ElementTree as ET

from typing import Any, cast, Callable, Dict, Optional, List, Union, Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.index.DataDictionary import DataDictionary
    from collections.abc import ValuesView

class JTypeDictionary(object):

    def __init__(self, jd: "DataDictionary", xnode: ET.Element):
        self.jd = jd
        self.string_table: IndexedTable[JT.StringConstant] = IndexedTable('string-table')
        self.class_name_table: IndexedTable[Classname] = IndexedTable('class-name-table')
        self.object_type_table: IndexedTable[JObjectTypeBase] = IndexedTable('object-type-table')
        self.value_type_table: IndexedTable[JValueTypeBase] = IndexedTable('value-type-table')
        self.method_descriptor_table: IndexedTable[MethodDescriptor] = IndexedTable('method-descriptor-table')
        self.descriptor_table: IndexedTable[JMethodDescriptorTypeBase] = IndexedTable('descriptor-table')
        self.field_signature_data_table: IndexedTable[FieldSignature] = IndexedTable('field-signature-data-table')
        self.method_signature_data_table: IndexedTable[MethodSignature] = IndexedTable('method-signature-data-table')
        self.class_field_signature_data_table: IndexedTable[ClassFieldSignature] = IndexedTable('class-field-signature-data-table')
        self.class_method_signature_data_table: IndexedTable[ClassMethodSignature] = IndexedTable('class-method-signature-data-table')
        self.constant_value_table: IndexedTable[JConstValueTypeBase] = IndexedTable('constant-value-table')
        self.method_handle_type_table: IndexedTable[JMethodHandleTypeBase] = IndexedTable('method-handle-type-table')
        self.constant_table: IndexedTable[JConstTypeBase] = IndexedTable('constant-table')
        self.bootstrap_argument_table: IndexedTable[JBootstrapArgumentTypeBase] = IndexedTable('bootstrap-argument-table')
        self.bootstrap_method_data_table: IndexedTable[JT.BootstrapMethodData] = IndexedTable('bootstrap-method-data-table')
        self.tables: List[Tuple[IndexedTableSuperclass, Callable[[ET.Element], None]]] = [
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

    def get_fields(self) -> "ValuesView[ClassFieldSignature]":
        return self.class_field_signature_data_table.indextable.values()

    def get_methods(self) -> "ValuesView[ClassMethodSignature]":
        return self.class_method_signature_data_table.indextable.values()

    def get_string(self, ix: int) -> JT.StringConstant: return self.string_table.retrieve(ix)

    def get_class_name(self, ix: int) -> Classname: return self.class_name_table.retrieve(ix)

    def get_field_signature_data(self, ix: int) -> FieldSignature: return self.field_signature_data_table.retrieve(ix)

    def get_class_field_signature_data(self, ix: int) -> ClassFieldSignature:
        return self.class_field_signature_data_table.retrieve(ix)

    def get_method_signature_data(self, ix: int) -> MethodSignature:
        return self.method_signature_data_table.retrieve(ix)

    def get_class_method_signature_data(self, ix: int) -> ClassMethodSignature:
        return self.class_method_signature_data_table.retrieve(ix)

    def get_cms_index(self, tags: List[str], args: List[int]) -> int:
        key = IT.get_key(tags,args)
        if self.class_method_signature_data_table.has_key(key):
            return self.class_method_signature_data_table.get_index(key)
        else:
            raise UF.CHJError(str(key) + 'missing from class-method-signature-data-table')

    def get_object_type(self, ix: int) -> JObjectTypeBase: return self.object_type_table.retrieve(ix)

    def get_value_type(self, ix: int) -> JValueTypeBase: return self.value_type_table.retrieve(ix)

    def get_method_descriptor(self, ix: int) -> MethodDescriptor: return self.method_descriptor_table.retrieve(ix)

    def get_descriptor(self, ix: int) -> JMethodDescriptorTypeBase: return self.descriptor_table.retrieve(ix)

    def get_constant(self, ix: int) -> JConstTypeBase: return self.constant_table.retrieve(ix)

    def get_constant_value(self, ix: int) -> JConstValueTypeBase: return self.constant_value_table.retrieve(ix)

    def get_method_handle_type(self, ix: int) -> JMethodHandleTypeBase: return self.method_handle_type_table.retrieve(ix)

    def get_bootstrap_argument(self, ix: int) -> JBootstrapArgumentTypeBase:
        return self.bootstrap_argument_table.retrieve(ix)

    def write_xml(self, node: ET.Element) -> None:
        def f(n: ET.Element, r: Any) -> None: 
            r.write_xml(n)
        for (t,_) in self.tables:
            tnode = ET.Element(t.name)
            cast(IndexedTable[IndexedTableValue], t).write_xml(tnode,f)
            node.append(tnode)

    def __str__(self) -> str:
        lines = []
        for (t,_) in self.tables:
            if t.size() > 0:
                lines.append(str(t))
        return '\n'.join(lines)

    # ----------------------- Initialize dictionary from file ------------------
 
    def initialize(self, xnode: Optional[ET.Element], force:bool= False) -> None:
        if xnode is None: return
        for (t,f) in self.tables:
            t.reset()
            f(UF.safe_find(xnode, t.name, t.name + ' missing from xml'))
           
    def _read_xml_string_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.StringConstant:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.StringConstant(*args)
        self.string_table.read_xml(txnode,'n',get_value)

    def _read_xml_class_name_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> Classname:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return Classname(*args)
        self.class_name_table.read_xml(txnode,'n',get_value)

    def _read_xml_object_type_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JObjectTypeBase:
            return JD.construct_j_dictionary_record(*((self,) + IT.get_rep(node)), JObjectTypeBase)
            
        self.object_type_table.read_xml(txnode,'n',get_value)

    def _read_xml_value_type_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JValueTypeBase:
            return JD.construct_j_dictionary_record(*((self,) + IT.get_rep(node)), JValueTypeBase)
        self.value_type_table.read_xml(txnode,'n',get_value)

    def _read_xml_method_descriptor_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> MethodDescriptor:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return MethodDescriptor(*args)
        self.method_descriptor_table.read_xml(txnode,'n',get_value)

    def _read_xml_field_signature_data_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> FieldSignature:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return FieldSignature(*args)
        self.field_signature_data_table.read_xml(txnode,'n',get_value)

    def _read_xml_class_field_signature_data_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> ClassFieldSignature:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return ClassFieldSignature(*args)
        self.class_field_signature_data_table.read_xml(txnode,'n',get_value)

    def _read_xml_method_signature_data_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> MethodSignature:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return MethodSignature(*args)
        self.method_signature_data_table.read_xml(txnode,'n',get_value)

    def _read_xml_class_method_signature_data_table(self,txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> ClassMethodSignature:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return ClassMethodSignature(*args)
        self.class_method_signature_data_table.read_xml(txnode,'n',get_value)            

    def _read_xml_descriptor_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JMethodDescriptorTypeBase:
            return JD.construct_j_dictionary_record(*((self,) + IT.get_rep(node)), JMethodDescriptorTypeBase)
        self.descriptor_table.read_xml(txnode,'n',get_value)

    def _read_xml_constant_value_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JConstValueTypeBase:
            return JD.construct_j_dictionary_record(*((self,) + IT.get_rep(node)), JConstValueTypeBase)
        self.constant_value_table.read_xml(txnode,'n',get_value)

    def _read_xml_method_handle_type_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JMethodHandleTypeBase:
            return JD.construct_j_dictionary_record(*((self,) + IT.get_rep(node)), JMethodHandleTypeBase)
        self.method_handle_type_table.read_xml(txnode,'n',get_value)

    def _read_xml_constant_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JConstTypeBase:
            return JD.construct_j_dictionary_record(*((self,) + IT.get_rep(node)), JConstTypeBase)
        self.constant_table.read_xml(txnode,'n',get_value)

    def _read_xml_bootstrap_argument_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JBootstrapArgumentTypeBase:
            return JD.construct_j_dictionary_record(*((self,) + IT.get_rep(node)), JBootstrapArgumentTypeBase)
        self.bootstrap_argument_table.read_xml(txnode,'n',get_value)

    def _read_xml_bootstrap_method_data_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.BootstrapMethodData:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.BootstrapMethodData(*args)
        self.bootstrap_method_data_table.read_xml(txnode,'n',get_value)
        

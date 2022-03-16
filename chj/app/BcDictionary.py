# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2020 Kestrel Technology LLC
# Copyright (c) 2021 Andrew McGraw
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
import chj.util.fileutil as UF

import chj.app.Bytecode as BC
import chj.app.BcDictionaryRecord as BCD

from typing import Any, Callable, cast, Dict, List, Optional, Tuple, TYPE_CHECKING

from chj.util.IndexedTable import (
    IndexedTableValue
)

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.index.DataDictionary import DataDictionary
    from chj.app.JavaClass import JavaClass
    import xml.etree.ElementTree as ET

class BcDictionary(object):

    def __init__(self, 
            jclass: "JavaClass",
            xnode: "ET.Element"):
        self.jclass = jclass                          # JavaClass
        self.jd: "DataDictionary" = jclass.jd         # DataDictionary
        self.pc_list_table: IT.IndexedTable[BC.BcPcList] = IT.IndexedTable('pc-list-table')
        self.slot_table: IT.IndexedTable[BC.BcSlot] = IT.IndexedTable('slot-table')
        self.slot_list_table: IT.IndexedTable[BC.BcSlotList] = IT.IndexedTable('slot-list-table')
        self.opcode_table: IT.IndexedTable[BC.JBytecodeBase] = IT.IndexedTable('opcode-table')
        self.tables: List[Tuple[IT.IndexedTableSuperclass, Callable[[ET.Element], None]]] = [
            (self.pc_list_table, self._read_xml_pc_list_table),
            (self.slot_table, self._read_xml_slot_table),
            (self.slot_list_table, self._read_xml_slot_list_table),
            (self.opcode_table, self._read_xml_opcode_table) ]
        self.initialize(xnode)

    def get_opcode(self, ix: int) -> BC.JBytecodeBase: return self.opcode_table.retrieve(ix)

    def get_pc_list(self, ix: int) -> BC.BcPcList: 
        return self.pc_list_table.retrieve(ix)

    def get_slot(self, ix: int) -> BC.BcSlot: return self.slot_table.retrieve(ix)

    def get_slots(self, ix: int) -> BC.BcSlotList: return self.slot_list_table.retrieve(ix)

    def write_xml(self, node: "ET.Element") -> None:
        def f(n: "ET.Element", r: Any) -> None:
            r.write_xml(n)
        for (t,_) in self.tables:
            tnode = ET.Element(t.name)
            cast(IT.IndexedTable[IndexedTableValue], t).write_xml(tnode,f)
            node.append(tnode)

    def __str__(self) -> str:
        lines = []
        for (t,_) in self.tables:
            if t.size() > 0:
                lines.append(str(t))
        return '\n'.join(lines)

    # ----------------------- Initialize dictionary from file ------------------
 
    def initialize(self, xnode: Optional["ET.Element"], force: bool=False) -> None:
        if xnode is None: return
        for (t,f) in self.tables:
            t.reset()
            f(UF.safe_find(xnode, t.name, t.name + ' missing from xml'))

    def _read_xml_pc_list_table(self, txnode: "ET.Element") -> None:
        def get_value(node : "ET.Element") -> BC.BcPcList:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return BC.BcPcList(*args)
        self.pc_list_table.read_xml(txnode,'n',get_value)

    def _read_xml_slot_table(self, txnode: "ET.Element") -> None:
        def get_value(node : "ET.Element") -> BC.BcSlot:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return BC.BcSlot(*args)
        self.slot_table.read_xml(txnode,'n',get_value)

    def _read_xml_slot_list_table(self, txnode: "ET.Element") -> None:
        def get_value(node: "ET.Element") -> BC.BcSlotList:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return BC.BcSlotList(*args)
        self.slot_list_table.read_xml(txnode,'n',get_value)

    def _read_xml_opcode_table(self, txnode: "ET.Element") -> None:
        def get_value(node: "ET.Element") -> BC.JBytecodeBase:
            rep = IT.get_rep(node)
            if BCD.is_bytecode(*((self,) + rep)):
                return BCD.construct_bytecode_dictionary_record(*((self,) + rep))
            #if BCD.is_bytecode(*((self,) + rep), BC.JBytecodeConstBase):
            #    return BCD.construct_bytecode_dictionary_record(*((self,) + rep), BC.JBytecodeConstBase)
            #elif BCD.is_bytecode(*((self,) + rep), BC.JBytecodeBase):
            #    return BCD.construct_bytecode_dictionary_record(*((self,) + rep), BC.JBytecodeBase)
            else:
                return BC.BcInstruction(*((self,) + rep))
        self.opcode_table.read_xml(txnode,'n',get_value)

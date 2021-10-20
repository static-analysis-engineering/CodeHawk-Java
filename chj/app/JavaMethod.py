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

import chj.util.fileutil as UF

from chj.app.Cfg import Cfg
from chj.app.ExceptionTable import ExceptionTable
from chj.app.Instruction import Instruction
from chj.app.Loop import Loop
from chj.app.MethodInvs import MethodInvs
from chj.app.Vartable import Vartable

from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import KeysView, ValuesView
    from chj.app.JavaClass import JavaClass
    from chj.app.Cfg import BBlock
    from chj.index.Classname import Classname
    from chj.index.DataDictionary import DataDictionary
    from chj.index.FieldSignature import FieldSignature
    import xml.etree.ElementTree as ET
    import chj.index.Taint as T

    TAINT_NODE_TYPES = Union[T.FieldTaintNode,
                    T.VariableTaintNode,
                    T.VariableEqTaintNode,
                    T.CallTaintNode,
                    T.UnknownCallTaintNode,
                    T.ObjectFieldTaintNode,
                    T.ConditionalTaintNode,
                    T.SizeTaintNode,
                    T.RefEqualTaintNode]

    TORIGIN_CONSTRUCTOR_TYPE = Union[T.VariableTaint,
                            T.FieldTaint,
                            T.CallerTaint,
                            T.TopTargetTaint,
                            T.StubTaint]

class JavaMethod(object):
    """Analysis results for a method.

    This class is initialized with the xml node for the method from the
    class analysis results file, for performance reasons. Four additional
    method results files are available:
    - _bc (bytecode) contains the cfg, variable table, and byte code instructions
    _ _invs (invariants) contains the location invariants at each pc
    - _taint contains taint information for each variable at each location
    - _loops contains detailed information on each loop in the method
    These files are loaded on demand when a related request for data is made.
    """

    def __init__(self, jclass: "JavaClass", xnode: "ET.Element") -> None:
        self.jclass = jclass                                    # JavaClass
        self.jd: "DataDictionary" = jclass.jd                   # DataDictionary
        self.xnode = xnode                                      # class file xnode
        self.access = xnode.get('access')
        self.loops: Dict[int, Loop] = {}                        # first-pc -> Loop
        self.cfg: Optional[Cfg] = None                          # Cfg
        self.instructions: Dict[int, Instruction] = {}          # pc -> Instruction
        self.exceptiontable: Optional[ExceptionTable] = None    # ExceptionTable
        self.variabletable: Optional[Vartable] = None
        self.taintedvariables: Dict[int, List["T.VariableTaintNode"]] = {}          # pc -> DTaintedVariables
        self.invariants: Optional[MethodInvs] = None            # MethodInvs
        self._read_method_bytecode()
        self._initialize_loops()                                # extract from class file xnode
        self._initialize_tainted_variables()
        self._read_method_invariants()

    @property
    def cmsix(self) -> int:
        cmsix = self.xnode.get('cmsix')
        if cmsix is None:
            raise UF.CHJError("cmsix missing from xml")
        else:
            return int(cmsix)

    def get_method_name(self) -> str: return self.jd.get_cms(self.cmsix).methodname

    def get_name(self) -> str: return self.jd.get_cms(self.cmsix).methodname

    def get_qname(self) -> str: return self.jd.get_cms(self.cmsix).get_qname()

    def get_aqname(self) -> str: return self.jd.get_cms(self.cmsix).get_aqname()

    def get_method_signature_string(self) -> str:
        return self.jd.get_cms(self.cmsix).get_signature()

    def get_exception_table(self) -> Optional[ExceptionTable]:
        self._read_method_bytecode()
        return self.exceptiontable

    def get_pcs(self) -> List[int]:
        self._read_method_bytecode()
        return sorted(self.instructions.keys())

    def get_loops(self) -> "ValuesView[Loop]":
        return self.loops.values()

    def get_loop_depth(self, pc: int) -> int:
        result = 0
        for loop in self.get_loops():
            if pc >= loop.first_pc and pc <= loop.last_pc:
                result += 1
        return result

    def get_loop_count(self) -> int:
        loops_node = UF.safe_find(self.xnode, 'loops', 'loops not found in xml for ' + self.get_name())
        return UF.safe_get(loops_node, 'count', 'loop count not found in xml for ' + self.get_name(), int)

    def get_max_depth(self) -> int:
        return int(self.xnode.get('max-depth','0'))

    def get_invariants(self) -> Optional[MethodInvs]:
        self._read_method_invariants()
        return self.invariants

    def get_cfg(self) -> Optional[Cfg]:
        self._read_method_bytecode()
        return self.cfg

    def get_conditions(self) -> List[Tuple[str, List[int]]]:
        if self.is_abstract(): return []
        self._read_method_bytecode()
        result = []
        def f(b: "BBlock") -> None:
            if b.has_conditions():
                result.append((b.get_tcond(),b.get_successor_loop_level_counts()))
        self.cfg.iter_blocks(f)
        return result

    def get_instruction(self, pc: int) -> Instruction:
        self._read_method_bytecode()
        return self.instructions[pc]

    def get_instructions(self) -> "ValuesView[Instruction]":
        self._read_method_bytecode()
        return self.instructions.values()

    def iter_instructions(self, f:Callable[[int, Instruction], None]) -> None:
        self._read_method_bytecode()
        for pc in self.instructions: f(pc,self.instructions[pc])

    def get_next_pc(self, pc: int) -> int:
        pcs = self.get_pcs()
        index = pcs.index(pc)
        if index < len(pcs) - 1:
            return pcs[index + 1]

    def get_slot_src_value(self, pc: int):
        if pc == -1: return 'exn object'
        return self.get_instruction(pc).get_result_value()

    def get_variable_name(self, name: str, pc: int) -> str:
        self._read_method_bytecode()
        if self.variabletable is None: return name
        if name.startswith('r'):
            try:
                index = int(name[1:])
                vname = self.variabletable.get_name(index,pc)
                if vname is None: return name
                return vname
            except:
                return name
        else:
            return name

    def get_loop(self, pc: int) -> Loop:
        if pc in self.loops:
            return self.loops[pc]
        else:
            raise UF.CHJError(str(self) + ' has no loop at pc: ' + str(pc))

    def count_recursive_calls(self) -> int:
        recursive_calls_count = 0
        for i in self.get_instructions():
            if i.is_call():
                if (self.get_qname() == i.getcallee()
                        and self.get_method_signature_string() == i.jmethod.get_method_signature_string()):
                    recursive_calls_count += 1
        return recursive_calls_count

    def has_calls(self) -> bool:
        return any(i.is_call() for i in self.get_instructions())

    def get_callee_cmsixs(self) -> List[int]:
        result = []
        def f(_: Any, i: Instruction) -> None:
            if i.is_call(): result.extend(i.get_cmsix_targets())
        self.iter_instructions(f)
        return result

    def is_abstract(self) -> bool:
        return (self.xnode.get('abstract','no') == 'yes')

    def is_loop_head(self,pc: int) -> bool:
        return pc in self.loops

    def has_exception_table(self) -> bool:
        self._read_method_bytecode()
        return (not self.exceptiontable is None)

    def get_tainted_variables(self, pc: int) -> List["T.VariableTaintNode"]:
        if pc in self.taintedvariables:
            return self.taintedvariables[pc]
        else:
            return []

    def get_variable_taint(self, name: str, pc: int) -> Optional["T.VariableTaintNode"]:
        tvars = self.get_tainted_variables(pc)
        if not tvars is None:
            for tv in tvars:
                if tv.get_variable().get_name() == name: return tv
        return None

    def get_loaded_strings(self, substring: str=None) -> List[Tuple[int, str]] :
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_load_string():
                s = i.get_string_constant().get_string()
                if substring is None or substring in s:
                    results.append((pc,i.get_string_constant().get_string()))
        self.iter_instructions(f)
        return results

    def get_loaded_string_instructions(self) -> List[Instruction]:
        results = []
        def f(_: int, i: Instruction) -> None:
            if i.is_load_string(): results.append(i)
        self.iter_instructions(f)
        return results

    def get_object_field_writes(self) -> List[Tuple[int, "Classname", "FieldSignature"]]:
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_put_field(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_object_field_reads(self) -> List[Tuple[int, "Classname", "FieldSignature"]]:
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_get_field(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_static_initializers(self) -> List[Tuple[int, "Classname", "FieldSignature"]]:
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_put_static(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_static_field_readers(self) -> List[Tuple[int, "Classname", "FieldSignature"]]:
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_get_static(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_objects_created(self) -> List[Tuple[int, Instruction]]:
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_object_created():results.append((pc,i))
        self.iter_instructions(f)
        return results

    def get_named_method_calls(self, s: str) -> List[Tuple[int, Instruction]]:
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_call():
                signature = i.get_signature()
                if signature.name == s:
                    results.append((pc,i))
        self.iter_instructions(f)
        return results

    # return instructions that call a method on a given class
    def get_class_method_calls(self, classname: str) -> List[Tuple[int, Instruction]]:
        results = []
        def f(pc: int, i: Instruction) -> None:
            if i.is_call():
                if i.has_targets():
                    if classname in [ str(s) for s in i.tgts.get_class_names() ]:
                        results.append((pc,i))
        self.iter_instructions(f)
        return results

    def as_dictionary(self) -> Dict[str, str]:
        self._read_method_bytecode()
        result = {}
        for i in sorted(self.instructions):
            result[str(i)] = str(self.instructions[i])
        return result

    def as_list(self) -> List[List[str]]:
        self._read_method_bytecode()
        lines = []
        for i in sorted(self.instructions):
            lines.append([str(i), str(self.instructions[i])])
        return lines

    def __str__(self) -> str:
        self._read_method_bytecode()
        lines = []
        lines.append(self.get_qname())
        lines.append(str(self.variabletable))
        for i in sorted(self.instructions):
            lines.append(str(i).rjust(4) + '  ' + str(self.instructions[i]))
        return '\n'.join(lines)
        

    def _initialize_loops(self) -> None:
        for l in UF.safe_find(self.xnode, 'loops', 'loops missing from xml for ' + self.get_name()).findall('loop'):
            looppc = UF.safe_get(l, 'first-pc', 'first-pc missing from xml for loop in ' + self.get_name(), int)
            self.loops[looppc] = Loop(self,l)

    def _get_file_details(self) -> Tuple[str, str, str, str, str]:
        path = str(self.jclass.app.path)
        package = str(self.jclass.package)
        classname = str(self.jclass.get_name())
        methodname = str(self.get_method_name())
        cmsix = str(self.cmsix)
        return (path,package,classname,methodname,cmsix)

    def _initialize_tainted_variables(self) -> None:
        if len(self.taintedvariables) > 0: return
        if self.jd.ttd is None: return
        def f(i: int, n: "T.VariableTaintNode") -> None:
            if n.get_caller().index == self.cmsix:
                pc = n.get_pc()
                if not pc in self.taintedvariables: self.taintedvariables[pc] = []
                self.taintedvariables[pc].append(n)
        self.jd.ttd.iter_var_taint_node_types(f)

    def _read_method_bytecode(self) -> None:
        if self.is_abstract(): return
        if len(self.instructions) > 0: return

        (path,package,classname,methodname,id) = self._get_file_details()

        bcxnode = UF.get_app_methodsbc_xnode(path,package,classname,methodname,id)
        inode = bcxnode.find('instructions')
        if not inode is None:
            for i in inode.findall('instr'):
                pc = UF.safe_get(i, 'pc', 'pc missing from xml for instruction in method ' + self.get_qname(), int)
                xiopc = UF.safe_get(i, 'iopc', 'iopc missing from xml for ' + self.get_qname(), int)
                iopc = self.jclass.bcd.get_opcode(xiopc)
                xissdl = UF.safe_get(i, 'issdl', 'issdl missing from xml for ' + self.get_qname(), int)
                exprstack = self.jclass.bcd.get_slots(xissdl)
                if 'itgt' in i.attrib:
                    tgts = self.jd.cgd.read_xml_target(i)
                elif self.jd.has_call_target(self.cmsix,pc):
                    (_,tgts) = self.jd.get_call_target(self.cmsix,pc)
                else:
                    tgts = None
                instr = Instruction(self,pc,iopc,exprstack,tgts)
                self.instructions[pc] = instr
        
        vtnode = bcxnode.find('variable-table')
        if not vtnode is None:
            self.variabletable = Vartable(self,vtnode)

        cfgnode = bcxnode.find('cfg')
        if not cfgnode is None:
            self.cfg = Cfg(self,cfgnode)

        exnode = bcxnode.find('exception-handlers')
        if not exnode is None and (len(exnode.findall('handler')) > 0):
            self.exceptiontable = ExceptionTable(self,exnode)

    def _read_method_invariants(self) -> None:
        if self.is_abstract(): return
        if not self.invariants is None: return

        try:
            (path,package,classname,methodname,id) = self._get_file_details()
            invsnode = UF.get_app_methodsinvs_xnode(path,package,classname,methodname,id)
            self.invariants = MethodInvs(self,invsnode)
        except Exception as e:
            print('Unable to load ' + str(methodname) + ' in ' + str(classname) + ': ' + str(e))

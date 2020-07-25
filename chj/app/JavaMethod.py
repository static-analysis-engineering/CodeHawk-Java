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

    def __init__(self,jclass,xnode):
        self.jclass = jclass          # JavaClass
        self.jd = jclass.jd           # DataDictionary
        self.xnode = xnode            # class file xnode
        self.cmsix = int(self.xnode.get('cmsix'))
        self.access = xnode.get('access')
        self.loops = {}               # first-pc -> Loop
        self.cfg = None               # Cfg
        self.instructions = {}        # pc -> Instruction
        self.exceptiontable = None    # ExceptionTable
        self.variabletable = None
        self.taintedvariables = {}    # pc -> DTaintedVariables
        self.invariants = None        # MethodInvs
        self._read_method_bytecode()
        self._initialize_loops()      # extract from class file xnode
        self._initialize_tainted_variables()
        self._read_method_invariants()

    def get_method_name(self): return self.jd.get_cms(self.cmsix).methodname

    def get_name(self): return self.jd.get_cms(self.cmsix).methodname

    def get_qname(self): return self.jd.get_cms(self.cmsix).get_qname()

    def get_aqname(self): return self.jd.get_cms(self.cmsix).get_aqname()

    def get_method_signature_string(self):
        return self.jd.get_cms(self.cmsix).get_signature()

    def get_exception_table(self):
        self._read_method_bytecode()
        return self.exceptiontable

    def get_pcs(self):
        self._read_method_bytecode()
        return sorted(self.instructions.keys())

    def get_loops(self):
        return self.loops.values()

    def get_loop_depth(self,pc):
        result = 0
        for loop in self.get_loops():
            if pc >= loop.first_pc and pc <= loop.last_pc:
                result += 1
        return result

    def get_loop_count(self):
        return int(self.xnode.find('loops').get('count'))

    def get_max_depth(self):
        return int(self.xnode.get('max-depth','0'))

    def get_invariants(self):
        self._read_method_invariants()
        return self.invariants

    def get_cfg(self):
        self._read_method_bytecode()
        return self.cfg

    def get_conditions(self):
        if self.is_abstract(): return []
        self._read_method_bytecode()
        result = []
        def f(b):
            if b.has_conditions():
                result.append((b.get_tcond(),b.get_successor_loop_level_counts()))
        self.cfg.iter_blocks(f)
        return result

    def get_instruction(self,pc):
        self._read_method_bytecode()
        return self.instructions[pc]

    def get_instructions(self):
        self._read_method_bytecode()
        return self.instructions.values()

    def iter_instructions(self,f):
        self._read_method_bytecode()
        for pc in self.instructions: f(pc,self.instructions[pc])

    def get_next_pc(self,pc):
        pcs = self.get_pcs()
        index = pcs.index(pc)
        if index < len(pcs) - 1:
            return pcs[index + 1]

    def get_slot_src_value(self,pc):
        if pc == -1: return 'exn object'
        return self.get_instruction(pc).get_result_value()

    def get_variable_name(self,name,pc):
        self._read_method_bytecode()
        if self.vartable is None: return name
        if name.startswith('r'):
            try:
                index = int(name[1:])
                vname = self.vartable.get_name(index,pc)
                if vname is None: return name
                return vname
            except:
                return name
        else:
            return name

    def get_loop(self,pc):
        if pc in self.loops:
            return self.loops[pc]

    def count_recursive_calls(self):
        recursive_calls_count = 0
        for i in self.get_instructions():
            if i.iscall():
                if (self.getqname() == i.getcallee()
                        and self.get_method_signature_string() == i.jmethod.get_method_signature_string()):
                    recursive_calls_count += 1
        return recursive_calls_count

    def has_calls(self):
        return any(i.is_call() for i in self.get_instructions())

    def get_callee_cmsixs(self):
        result = []
        def f(_,i):
            if i.is_call(): result.extend(i.get_cmsix_targets())
        self.iter_instructions(f)
        return result

    def is_abstract(self):
        return (self.xnode.get('abstract','no') == 'yes')

    def is_loop_head(self,pc):
        return pc in self.loops

    def has_exception_table(self):
        self._read_method_bytecode()
        return (not self.exceptiontable is None)

    def get_tainted_variables(self,pc):
        if pc in self.taintedvariables:
            return self.taintedvariables[pc]
        else:
            return []

    def get_variable_taint(self,name,pc):
        tvars = self.get_tainted_variables(pc)
        if not tvars is None:
            for tv in tvars:
                if tv.get_variable().get_name() == name: return tv

    def get_loaded_strings(self,substring=None):
        results = []
        def f(pc,i):
            if i.is_load_string():
                s = i.get_string_constant().get_string()
                if substring is None or substring in s:
                    results.append((pc,i.get_string_constant().get_string()))
        self.iter_instructions(f)
        return results

    def get_loaded_string_instructions(self,s):
        results = []
        def f(i): 
            if i.is_load_string(s): results.append(i)
        self.iter_instructions(f)
        return results

    def get_object_field_writes(self):
        results = []
        def f(pc,i):
            if i.is_put_field(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_object_field_reads(self):
        results = []
        def f(pc,i):
            if i.is_get_field(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_static_initializers(self):
        results = []
        def f(pc,i):
            if i.is_put_static(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_static_field_readers(self):
        results = []
        def f(pc,i):
            if i.is_get_static(): results.append((pc,i.get_cn(),i.get_field()))
        self.iter_instructions(f)
        return results

    def get_objects_created(self):
        results = []
        def f(pc,i):
            if i.is_object_created():results.append((pc,i))
        self.iter_instructions(f)
        return results

    def get_named_method_calls(self,s):
        results = []
        def f(pc,i):
            if i.is_call():
                signature = i.get_signature()
                if signature.name == s:
                    results.append((pc,i))
        self.iter_instructions(f)
        return results

    # return instructions that call a method on a given class
    def get_class_method_calls(self,classname):
        results = []
        def f(pc,i):
            if i.is_call():
                if i.has_targets():
                    if classname in [ str(s) for s in i.tgts.get_class_names() ]:
                        results.append((pc,i))
        self.iter_instructions(f)
        return results

    def as_list(self):
        self._read_method_bytecode()
        lines = []
        for i in sorted(self.instructions):
            lines.append([str(i), str(self.instructions[i])])
        return lines

    def __str__(self):
        self._read_method_bytecode()
        lines = []
        lines.append(self.get_qname())
        lines.append(str(self.variabletable))
        for i in sorted(self.instructions):
            lines.append(str(i).rjust(4) + '  ' + str(self.instructions[i]))
        return '\n'.join(lines)
        

    def _initialize_loops(self):
        for l in self.xnode.find('loops').findall('loop'):
            self.loops[int(l.get('first-pc'))] = Loop(self,l)

    def _get_file_details(self):
        path = str(self.jclass.app.path)
        package = str(self.jclass.package)
        classname = str(self.jclass.get_name())
        methodname = str(self.get_method_name())
        cmsix = str(self.cmsix)
        return (path,package,classname,methodname,cmsix)

    def _initialize_tainted_variables(self):
        if len(self.taintedvariables) > 0: return
        if self.jd.ttd is None: return
        def f(i,n):
            if n.get_caller().index == self.cmsix:
                pc = n.get_pc()
                if not pc in self.taintedvariables: self.taintedvariables[pc] = []
                self.taintedvariables[pc].append(n)
        self.jd.ttd.iter_var_taint_node_types(f)

    def _read_method_bytecode(self):
        if self.is_abstract(): return
        if len(self.instructions) > 0: return

        (path,package,classname,methodname,id) = self._get_file_details()

        bcxnode = UF.get_app_methodsbc_xnode(path,package,classname,methodname,id)
        inode = bcxnode.find('instructions')
        if not inode is None:
            for i in inode.findall('instr'):
                pc = int(i.get('pc'))
                iopc = self.jclass.bcd.get_opcode(int(i.get('iopc')))
                exprstack = self.jclass.bcd.get_slots(int(i.get('issdl')))
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

    def _read_method_invariants(self):
        if self.is_abstract(): return
        if not self.invariants is None: return

        try:
            (path,package,classname,methodname,id) = self._get_file_details()
            invsnode = UF.get_app_methodsinvs_xnode(path,package,classname,methodname,id)
            self.invariants = MethodInvs(self,invsnode)
        except Exception as e:
            print('Unable to load ' + str(methodname) + ' in ' + str(classname) + ': ' + str(e))

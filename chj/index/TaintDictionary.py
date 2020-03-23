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

import chj.index.Taint as T


taint_origin_constructors = {
    'v': lambda x:T.VariableTaint(*x),
    'f': lambda x:T.FieldTaint(*x),
    'c': lambda x:T.CallerTaint(*x),
    't': lambda x:T.TopTargetTaint(*x),
    's': lambda x:T.StubTaint(*x)
    }

taint_node_type_constructors = {
    'f': lambda x:T.FieldTaintNode(*x),
    'v': lambda x:T.VariableTaintNode(*x),
    'q': lambda x:T.VariableEqTaintNode(*x),
    'c': lambda x:T.CallTaintNode(*x),
    'u': lambda x:T.UnknownCallTaintNode(*x),
    'o': lambda x:T.ObjectFieldTaintNode(*x),
    'j': lambda x:T.ConditionalTaintNode(*x),
    's': lambda x:T.SizeTaintNode(*x),
    'r': lambda x:T.RefEqualTaintNode(*x)
    }

class TaintDictionary(object):

    def __init__(self,jd,xnode):
        self.jd = jd                  # DataDictionary
        self.string_table = IT.IndexedTable('string-table')
        self.symbol_table = IT.IndexedTable('symbol-table')
        self.variable_table = IT.IndexedTable('variable-table')
        self.method_target_table = IT.IndexedTable('method-target-table')
        self.taint_origin_table = IT.IndexedTable('taint-origin-table')
        self.taint_origin_list_table = IT.IndexedTable('taint-origin-list-table')
        self.tainted_variable_table = IT.IndexedTable('tainted-variable-table')
        self.tainted_variable_ids_table = IT.IndexedTable('tainted-variable-ids-table')
        self.taint_node_type_table = IT.IndexedTable('taint-node-type-table')
        self.tables = [
            (self.string_table, self._read_xml_string_table),
            (self.symbol_table, self._read_xml_symbol_table),
            (self.variable_table, self._read_xml_variable_table),
            (self.method_target_table, self._read_xml_method_target_table),
            (self.taint_origin_table, self._read_xml_taint_origin_table),
            (self.taint_origin_list_table, self._read_xml_taint_origin_list_table),
            (self.tainted_variable_table, self._read_xml_tainted_variable_table),
            (self.tainted_variable_ids_table, self._read_xml_tainted_variable_ids_table),
            (self.taint_node_type_table, self._read_xml_taint_node_type_table)
            ]
        self.initialize(xnode)

    def get_string(self,ix): return self.string_table.retrieve(ix)

    def get_symbol(self,ix): return self.symbol_table.retrieve(ix)

    def get_variable(self,ix): return self.variable_table.retrieve(ix)

    def get_method_target(self,ix): return self.method_target_table.retrieve(ix)

    def get_taint_origin(self,ix): return self.taint_origin_table.retrieve(ix)

    def get_taint_origin_list(self,ix): return self.taint_origin_list_table.retrieve(ix)

    def get_tainted_variable(self,ix): return self.tainted_variable_table.retrieve(ix)

    def get_tainted_variable_ids(self,ix): return self.tainted_variable_ids_table.retrieve(ix)

    def get_taint_origins(self): return self.taint_origin_table.values()

    def get_taint_node_type(self,ix): return self.taint_node_type_table.retrieve(ix)

    def iter_taint_node_types(self,f): self.taint_node_type_table.iter(f)

    def iter_var_taint_node_types(self,f):
        def g(i,n):
            if n.is_var(): f(i,n)
            else: pass
        self.iter_taint_node_types(g)

    def read_xml_tainted_variable_ids(self,node,tag='itvids'):
        return self.get_tainted_variable_ids(int(node.get(tag)))

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
            return T.TStringConstant(*args)
        self.string_table.read_xml(txnode,'n',get_value)

    def _read_xml_symbol_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return T.TSymbol(*args)
        self.symbol_table.read_xml(txnode,'n',get_value)

    def _read_xml_variable_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return T.TVariable(*args)
        self.variable_table.read_xml(txnode,'n',get_value)

    def _read_xml_method_target_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return T.TMethodTarget(*args)
        self.method_target_table.read_xml(txnode,'n',get_value)

    def _read_xml_taint_origin_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return taint_origin_constructors[tag](args)
        self.taint_origin_table.read_xml(txnode,'n',get_value)

    def _read_xml_taint_origin_list_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return T.TaintOriginList(*args)
        self.taint_origin_list_table.read_xml(txnode,'n',get_value)

    def _read_xml_tainted_variable_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return T.TaintedVariable(*args)
        self.tainted_variable_table.read_xml(txnode,'n',get_value)

    def _read_xml_tainted_variable_ids_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            args = (self,) + rep
            return T.TaintedVariableIds(*args)
        self.tainted_variable_ids_table.read_xml(txnode,'n',get_value)

    def _read_xml_taint_node_type_table(self,txnode):
        def get_value(node):
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return taint_node_type_constructors[tag](args)
        self.taint_node_type_table.read_xml(txnode,'n',get_value)

        
        

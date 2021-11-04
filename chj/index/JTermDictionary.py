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

from typing import Callable, cast, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.DataDictionary import DataDictionary

import chj.util.IndexedTable as IT
import chj.util.fileutil as UF

import chj.index.JTerm as JT

import xml.etree.ElementTree as ET

jterm_constructors: Dict[
    str,
    Callable[[Tuple["JTermDictionary", int, List[str], List[int]]], JT.JTermBase]   
] = {
    'xv': lambda x:JT.JTAuxiliaryVar(*x),
    'lv': lambda x:JT.JTLocalVar(*x),
    'lc': lambda x:JT.JTLoopCounter(*x),
    'c' : lambda x:JT.JTConstant(*x),
    'sf': lambda x:JT.JTStaticFieldValue(*x),
    'of': lambda x:JT.JTObjectFieldValue(*x),
    'bc': lambda x:JT.JTBoolConstant(*x),
    'fc': lambda x:JT.JTFloatConstant(*x),
    'sc': lambda x:JT.JTermStringConstant(*x),
    'al': lambda x:JT.JTArrayLength(*x),
    'sl': lambda x:JT.JTStringLength(*x),
    'si': lambda x:JT.JTSize(*x),
    'ar': lambda x:JT.JTArithmeticExpr(*x),
    'symc': lambda x:JT.JTSymbolicConstant(*x)
    }

class JTermDictionary(object):

    def __init__(self, jd: "DataDictionary", xnode: ET.Element):
        self.jd = jd
        self.symbolic_jterm_constant_table: IT.IndexedTable[JT.JTSymbolicJTermConstant] = IT.IndexedTable('symbolic-jterm-constant-table')
        self.string_table: IT.IndexedTable[JT.JTStringConstant] = IT.IndexedTable('string-table')
        self.numerical_table: IT.IndexedTable[JT.JTNumerical] = IT.IndexedTable('numerical-table')
        self.float_table: IT.IndexedTable[JT.JTFloat] = IT.IndexedTable('float-table')
        self.jterm_table: IT.IndexedTable[JT.JTermBase] = IT.IndexedTable('jterm-table')
        self.relational_expr_table: IT.IndexedTable[JT.JTRelationalExpr] = IT.IndexedTable('relational-expr-table')
        self.jterm_list_table: IT.IndexedTable[JT.JTermList] = IT.IndexedTable('jterm-list-table')
        self.relational_expr_list_table: IT.IndexedTable[JT.JTRelationalExprList] = IT.IndexedTable('relational-expr-list-table')
        self.jterm_range_table: IT.IndexedTable[JT.JTermRange] = IT.IndexedTable('jterm-range-table')
        self.tables: List[Tuple[IT.IndexedTableSuperclass, Callable[[ET.Element], None]]] = [
            (self.symbolic_jterm_constant_table, self._read_xml_symbolic_jterm_constant_table),
            (self.string_table, self._read_xml_string_table),
            (self.numerical_table, self._read_xml_numerical_table),
            (self.float_table, self._read_xml_float_table),
            (self.jterm_table, self._read_xml_jterm_table),
            (self.relational_expr_table, self._read_xml_relational_expr_table),
            (self.jterm_list_table, self._read_xml_jterm_list_table),
            (self.relational_expr_list_table, self._read_xml_relational_expr_list_table),
            (self.jterm_range_table, self._read_xml_jterm_range_table) ]
        self.initialize(xnode)

    def get_symbolic_jterm_constant(self, ix: int) -> JT.JTSymbolicJTermConstant:
        return self.symbolic_jterm_constant_table.retrieve(ix)

    def get_string(self, ix: int) -> JT.JTStringConstant:
        return self.string_table.retrieve(ix)

    def get_numerical(self, ix: int) -> JT.JTNumerical:
        return self.numerical_table.retrieve(ix)

    def get_float(self, ix: int) -> JT.JTFloat:
        return self.float_table.retrieve(ix)

    def get_jterm(self, ix: int) -> JT.JTermBase: return self.jterm_table.retrieve(ix)

    def get_relational_expr(self, ix: int) -> JT.JTRelationalExpr:
        return self.relational_expr_table.retrieve(ix)

    def get_jterm_list(self, ix: int) -> JT.JTermList:
        return self.jterm_list_table.retrieve(ix)

    def get_relational_expr_list(self, ix: int) -> JT.JTRelationalExprList:
        return self.relational_expr_list_table.retrieve(ix)

    def get_jterm_range(self, ix: int) -> JT.JTermRange:
        return self.jterm_range_table.retrieve(ix)

    def index_numerical(self, v: int) -> int:
        tags = [ str(v) ]
        def f(index: int, key: Tuple[str, str]) -> JT.JTNumerical: 
            return JT.JTNumerical(self,index,tags,[])
        return self.numerical_table.add(IT.get_key(tags,[]),f)

    def mk_numerical(self, v: int) -> JT.JTNumerical:
        return self.get_numerical(self.index_numerical(v))

    def index_float(self, v: float) -> int:
        tags = [ str(v) ]
        def f(index: int, key: Tuple[str, str]) -> JT.JTFloat: 
            return JT.JTFloat(self,index,tags,[])
        return self.float_table.add(IT.get_key(tags,[]),f)

    def index_float_constant(self, v: float) -> int:
        tags = [ 'fc' ]
        args = [ self.index_float(float(v)) ]
        def f(index: int, key: Tuple[str, str]) -> JT.JTFloatConstant: 
            return JT.JTFloatConstant(self,index,tags,args)
        return self.jterm_table.add(IT.get_key(tags,args),f)

    def mk_float_constant(self, v: float) -> JT.JTFloatConstant:
        return cast(JT.JTFloatConstant, self.get_jterm(self.index_float_constant(v)))

    def index_constant_jterm(self, v):
        tags = ['c']
        args = [ self.index_numerical(v) ]
        def f(index,key): return JT.JTConstant(self,index,tags,args)
        return self.jterm_table.add(IT.get_key(tags,args),f)

    def mk_constant_jterm(self, v: int) -> JT.JTermBase:
        return self.get_jterm(self.index_constant_jterm(v))

    def index_arithmetic_jterm(self,jt1,jt2,op):
        tags = ['ar',op]
        args = [ jt1.index, jt2.index ]
        def f(index,key): return JT.JTArithmeticExpr(self,index,tags,args)
        return self.jterm_table.add(IT.get_key(tags,args),f)

    def mk_arithmetic_jterm(self,jt1,jt2,op):
        return self.get_jterm(self.index_arithmetic_jterm(jt1,jt2,op))

    def read_xml_jterm(self,node,tag='ijt'):
        return self.get_jterm(int(node.get(tag)))

    def read_xml_relational_expr_list(self,node,tag='irel'):
        return self.get_relational_expr_list(int(node.get(tag)))

    def write_xml(self,node):
        def f(n,r):r.write_xml(n)
        for (t,_) in self.tables:
            tnode = ET.Element(t.name)
            t.write_xml(tnode,f)
            node.append(tnode)

    def __str__(self) -> str:
        lines = []
        for (t,_) in self.tables:
            if t.size() > 0:
                lines.append(str(t))
        return '\n'.join(lines)

    # ----------------------- Initialize dictionary from file ------------------
 
    def initialize(self, xnode: Optional[ET.Element], force: bool=False) -> None:
        if xnode is None: return
        for (t,f) in self.tables:
            t.reset()
            f(UF.safe_find(xnode, t.name, t.name + ' missing from xml'))
           
    def _read_xml_string_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTStringConstant:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTStringConstant(*args)
        self.string_table.read_xml(txnode,'n',get_value)

    def _read_xml_symbolic_jterm_constant_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTSymbolicJTermConstant:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTSymbolicJTermConstant(*args)
        self.symbolic_jterm_constant_table.read_xml(txnode,'n',get_value)

    def _read_xml_numerical_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTNumerical:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTNumerical(*args)
        self.numerical_table.read_xml(txnode,'n',get_value)

    def _read_xml_float_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTFloat:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTFloat(*args)
        self.float_table.read_xml(txnode,'n',get_value)

    def _read_xml_jterm_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTermBase:
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return jterm_constructors[tag](args)
        self.jterm_table.read_xml(txnode,'n',get_value)

    def _read_xml_relational_expr_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTRelationalExpr:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTRelationalExpr(*args)
        self.relational_expr_table.read_xml(txnode,'n',get_value)

    def _read_xml_jterm_list_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTermList:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTermList(*args)
        self.jterm_list_table.read_xml(txnode,'n',get_value)

    def _read_xml_relational_expr_list_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTRelationalExprList:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTRelationalExprList(*args)
        self.relational_expr_list_table.read_xml(txnode,'n',get_value)

    def _read_xml_jterm_range_table(self, txnode: Optional[ET.Element]) -> None:
        def get_value(node: ET.Element) -> JT.JTermRange:
            rep = IT.get_rep(node)
            args = (self,) + rep
            return JT.JTermRange(*args)
        self.jterm_range_table.read_xml(txnode,'n',get_value)
            
    
        
        
        

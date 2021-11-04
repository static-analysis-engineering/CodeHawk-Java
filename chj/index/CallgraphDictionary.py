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

import chj.util.IndexedTable as IT
import chj.util.fileutil as UF

import chj.index.JDictionaryRecord as JD

from typing import Any, Callable, Dict, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.MethodSignature import MethodSignature
    from chj.index.DataDictionary import DataDictionary
    import xml.etree.ElementTree as ET

class CallgraphTargetBase(JD.JDictionaryRecord):

    def __init__(self,
            cgd: "CallgraphDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        JD.JDictionaryRecord.__init__(self,index,tags,args)
        self.cgd = cgd
        self.cnixs: List[int] = []

    def has_application_targets(self) -> bool: return False

    def get_application_targets(self) -> List[int]: return []

    def get_class_names(self) -> List[str]: return []

    def is_non_virtual_target(self) -> bool: return False

    def is_virtual_target(self) -> bool: return False

    def is_empty_target(self) -> bool: return False

    def __str__(self) -> str: return 'jdcgtargetbase'

class NonVirtualTarget(CallgraphTargetBase):

    def __init__(self,
            cgd: "CallgraphDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        CallgraphTargetBase.__init__(self,cgd,index,tags,args)
        self.cnix = int(self.args[0])
        self.cnixs = [ self.cnix ]
        self.classname = self.cgd.jd.get_cn(self.cnix).get_name()
        self.targettype = self.tags[1]

    def get_class_names(self) -> List[str]: return [ self.classname ]

    def has_application_targets(self) -> bool:
        return self.cgd.jd.is_application_class(self.cnix)

    def get_application_targets(self) -> List[int]:
        if self.has_application_targets(): return [ self.cnix ]
        return []

    def is_non_virtual_target(self) -> bool: return True

    def __str__(self) -> str: return 'nv:' + str(str(self.classname))


class ConstrainedVirtualTargets(CallgraphTargetBase):

    def __init__(self,
            cgd: "CallgraphDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        CallgraphTargetBase.__init__(self, cgd, index, tags, args)
        self.cnixs = [ int(x) for x in self.args ]

    def get_class_names(self) -> List[str]:
        return [ str(self.cgd.jd.get_cn(x).get_name()) for x in self.cnixs ]

    def get_tag(self) -> str:  return self.tags[1]

    def get_length(self) -> int: return len(self.args)

    def has_application_targets(self) -> bool:
        return any( [ self.cgd.jd.is_application_class(cnix) for cnix in self.cnixs ])

    def get_application_targets(self) -> List[int]:
        return [ cnix for cnix in self.cnixs if self.cgd.jd.is_application_class(cnix) ]

    def is_virtual_target(self) -> bool: return True

    def __str__(self) -> str: return 'cv:' + '; '.join(self.get_class_names()) + ' (' + str(self.get_tag()) + ')'


class VirtualTargets(CallgraphTargetBase):

    def __init__(self,
            cgd: "CallgraphDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        CallgraphTargetBase.__init__(self,cgd,index,tags,args)
        self.cnixs = [ int(x) for x in self.args ]

    def get_class_names(self) -> List[str]:
        return [ str(self.cgd.jd.get_cn(x).get_name()) for x in self.cnixs ]

    def get_length(self) -> int: return len(self.args)

    def get_application_targets(self) -> List[int]:
        return [ cnix for cnix in self.cnixs if self.cgd.jd.is_application_class(cnix) ]

    def is_virtual_target(self) -> bool: return True

    def __str__(self) -> str: return 'v:' + ';'.join(self.get_class_names())


class EmptyTarget(CallgraphTargetBase):

    def __init__(self,
            cgd: "CallgraphDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        CallgraphTargetBase.__init__(self,cgd,index,tags,args)
        self.cnixs = []

    def is_interface(self) -> bool: return int(self.args[0]) == 1

    def get_cnix(self) -> int: return int(self.args[1])

    def get_msix(self) -> int: return int(self.args[2])

    def get_class_name(self) -> str:
        return self.cgd.jd.get_cn(self.get_cnix()).get_name()

    def get_class_names(self) -> List[str]: return [ self.get_class_name() ]

    def get_method_signature(self) -> "MethodSignature":
        return self.cgd.jd.get_ms(self.get_msix())

    def __str__(self) -> str:
        return 'empty:' + str(self.get_class_name()) + str(self.get_method_signature())
                                  
method_target_constructors: Dict[
    str,
    Callable[[Tuple["CallgraphDictionary", int, List[str], List[int]]], "CallgraphTargetBase"]
] = {
    'nv': lambda x: NonVirtualTarget(*x),
    'cv': lambda x: ConstrainedVirtualTargets(*x),
    'v':  lambda x: VirtualTargets(*x),
    'empty': lambda x: EmptyTarget(*x)
    }

class CallgraphDictionary(object):

    def __init__(self,
            jd: "DataDictionary",
            xnode: "ET.Element"):
        self.jd = jd
        self.target_table: IT.IndexedTable["CallgraphTargetBase"] = IT.IndexedTable('target-table')
        self.tables = [
            (self.target_table, self._read_xml_target_table)
            ]
        self.initialize(xnode)

    def get_target(self, ix: int) -> "CallgraphTargetBase": return self.target_table.retrieve(ix)

    def read_xml_target(self, node: "ET.Element", tag: str='itgt') -> "CallgraphTargetBase":
        return self.get_target(UF.safe_get(node, tag, 'tag missing from xml of CallgraphDictionary', int))

    def write_xml(self, node: "ET.Element") -> None:
        def f(n: ET.Element, r: Any) -> None:
            r.write_xml(n)
        for (t, _) in self.tables:
            tnode = ET.Element(t.name)
            t.write_xml(tnode, f)
            node.append(tnode)

    def __str__(self) -> str:
        lines = []
        for (t,_) in self.tables:
            if t.size() > 0:
                lines.append(str(t))
        return '\n'.join(lines)

    # ----------------------- Initialize dictionary from file ------------------
 
    def initialize(self, xnode: "ET.Element", force: bool=False) -> None:
        if xnode is None: return
        for (t,f) in self.tables:
            t.reset()
            f(UF.safe_find(xnode, t.name, 'Missing xml for table ' + t.name))

    def _read_xml_target_table(self, txnode: "ET.Element") -> None:
        def get_value(node: "ET.Element") -> "CallgraphTargetBase":
            rep = IT.get_rep(node)
            tag = rep[1][0]
            args = (self,) + rep
            return method_target_constructors[tag](args)
        self.target_table.read_xml(txnode,'n',get_value)
        

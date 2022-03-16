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

import xml.etree.ElementTree as ET

import chj.util.fileutil as UF
import chj.util.xmlutil as UX

from chj.cost.MethodCost import MethodCost

from typing import Callable, cast, Dict, List, Mapping, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.cost.CostMeasure import CostMeasure
    from chj.index.AppAccess import AppAccess
    from chj.index.DataDictionary import DataDictionary
    from chj.index.JTerm import JTermRange
    from collections.abc import KeysView
    from collections.abc import ValuesView
    from collections.abc import ItemsView

class CostModel():

    def __init__(self, app: "AppAccess") -> None:
        self.app = app                                      # AppAccess
        self.jd: "DataDictionary" = self.app.jd             # DataDictionary
        self.methodcosts: Mapping[int, MethodCost] = {}     # cmsix -> MethodCost
        self.constants: Dict[str, str] = {}                # name -> value
        self.originalconstants: Dict[str, str] = {}
        self._initialize()

    def iter(self, f: Callable[[MethodCost], None]) -> None:
        for m in self.methodcosts:
            f(self.methodcosts[m])

    def reinitialize(self) -> None: self._initialize()

    def get_method_cost(self, id: int) -> MethodCost:
        if id in self.methodcosts:
            return self.methodcosts[id]
        else:
            raise UF.CHJError("MethodCost missing for method " + str(id))

    def get_simplified_method_cost(self, id: int) -> Union[str, MethodCost]:
        if id in self.methodcosts:
            cost = self.methodcosts[id].methodcost
            if cost.is_top() or cost.is_value() or cost.is_range():
                return self.methodcosts[id]
            else:
                return "X"
        else:
            return "X"

    def get_top_method_costs(self) -> List[int]:
        result = []
        for cmsix in self.methodcosts:
            if self.methodcosts[cmsix].methodcost.cost.is_top():
                result.append(cmsix)
        return result

    def get_constant_method_costs(self) -> List[Tuple[int, int]]:
        result = []
        for cmsix in self.methodcosts:
            if self.methodcosts[cmsix].methodcost.is_value():
                result.append((cmsix,self.methodcosts[cmsix].methodcost.get_value()))
        result = sorted(result,key=(lambda c : c[1]))
        return result

    def get_range_method_costs(self) -> List[Tuple[int, Tuple[int, int]]]:
        result = []
        for cmsix in self.methodcosts:
            if (self.methodcosts[cmsix].methodcost.is_range()
                    and not self.methodcosts[cmsix].methodcost.is_value()):
                range = cast(Tuple[int, int], self.methodcosts[cmsix].methodcost.get_range())     #enforced by previous is_range() call
                result.append((cmsix, range))
        result = sorted(result,key=lambda x:x[1][1])
        return result

    def get_symbolic_method_costs(self) -> List[Tuple[int, "CostMeasure"]]:
        result = []
        for cmsix in self.methodcosts:
            cost = self.methodcosts[cmsix].methodcost
            if cost.is_top(): continue
            if cost.is_value(): continue
            if cost.is_range(): continue
            result.append((cmsix,cost))
        return result

    def get_constant_names(self) -> "KeysView[str]": return self.constants.keys()

    def get_constant_values(self) -> "ItemsView[str, str]": return self.constants.items()

    def get_constant_value(self, name: str) -> str:
        if name in self.constants:
            return self.constants[name]
        else:
            raise UF.CHJError("Constant value for " + name + " missing from xml.")

    def set_constant_value(self, name: str, v: str) -> None: self.constants[name] = v

    def get_unknown_methodcosts(self) -> int:
        return len(list(m for m in self.methodcosts
                        if self.methodcosts[m].methodcost.is_unknown()))
    
    def save_constants_file(self) -> None:
        doc = UX.dict_to_xmlpretty(self.constants,'constants','constant','name','value')
        if not doc is None:
            with open(UF.get_costmodel_constants_filename(self.app.path),'w') as fp:
                fp.write(doc)

    def restore_original_constants(self) -> None:
        for (name,value) in self.originalconstants.items():
            self.constants[name] = value

    def store_original_constants(self) -> None:
        xnode = UF.get_costmodel_constants_xnode(self.app.path)
        if not xnode is None:
            for x in xnode.findall('constant'):
                name = UF.safe_get(x, 'name', 'Name of constant not found', str)
                value = UF.safe_get(x, 'value', 'Cost value of ' + name + ' not found.', str)
                self.originalconstants[name] = value
        else:
            print('No constants file found')

    def __str__(self) -> str:
        lines = []
        for m in self.methodcosts:
            lines.append(str(self.methodcosts[m]))
        unknowncount = sum( [ 1 for m in self.methodcosts if self.methodcosts[m].methodcost.is_unknown() ])
        lines.append('Methods with unknown cost: ' + str(unknowncount))
        return '\n'.join(lines)

    def _initialize(self) -> None:
        self.methodcosts = {}
        for cnix in self.jd.appclassindices.values():
            c = self.jd.get_cn(cnix)
            try:
                xnode = UF.get_costclass_xnode(self.app.path,c.get_package_name(),c.get_simple_name())
            except UF.CHJError as e:
                print(str(e.wrap()))
                print('\nPlease make sure cost analysis has been performed with chj_analyze_cost.py.\n')
                exit(1)
            if not xnode is None:
                methodsnode = xnode.find('methods')
                if methodsnode is None:
                    raise UF.CHJError('Could not find methods in xml for class ' + str(c))
                for x in methodsnode.findall('method'):
                    if 'abstract' in x.attrib: continue
                    if 'imcost' in x.attrib:
                        mc = MethodCost(self,x)
                        cmsix = UF.safe_get(x, 'cmsix', 'Could not find cmsix in xml.', int)
                        self.methodcosts[cmsix] = mc
                xcc = xnode.find('constructors')
                if not xcc is None:
                    for x in xcc.findall('constructor'):
                        mc = MethodCost(self,x)
                        self.methodcosts[mc.cmsix] = mc



    

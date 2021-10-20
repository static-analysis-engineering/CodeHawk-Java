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

from typing import Tuple, TYPE_CHECKING

import chj.util.fileutil as UF

if TYPE_CHECKING:
    from chj.libsum.MethodSummary import MethodSummary
    import xml.etree.ElementTree as ET

class SummaryTimeCost(object):

    def __init__(self,
            methodsum: "MethodSummary",
            xnode: "ET.Element"):
        self.methodsum = methodsum
        self.xnode = xnode

    def is_constant_cost(self) -> bool:
        xcost = UF.safe_find(self.xnode, 'cost', self.methodsum.get_name() + ' cost missing from xml')
        return len(xcost) > 0 and xcost[0].tag == 'cn'

    def is_interval_cost(self) -> bool:
        xcost = UF.safe_find(self.xnode, 'cost', self.methodsum.get_name() + ' cost missing from xml')
        return 'lb' in xcost.attrib and 'ub' in xcost.attrib
            
    def is_from_model(self) -> bool:
        return 'src' in self.xnode.attrib and self.xnode.get('src') == 'model'

    def has_model_comparison_value(self) -> bool:
        return 'modelvalue' in self.xnode.attrib

    def has_calls(self) -> bool:
        return 'calls' in self.xnode.attrib and self.xnode.get('calls') == 'yes'

    def get_constant_cost(self) -> int:
        xcost = UF.safe_find(self.xnode, 'cost', self.methodsum.get_name() + ' cost missing from xml')
        xcn = UF.safe_find(xcost, 'cn', self.methodsum.get_name() + ' cn missing from xml')
        return int(xcn.text)

    def get_interval_cost(self) -> Tuple[int, int]:
        if self.is_interval_cost():
            xcost = UF.safe_find(self.xnode, 'cost', 'cost missing from xml for interval')
            lb = UF.safe_get(xcost, 'lb', 'lb missing from xml for interval', int)
            ub = UF.safe_get(xcost, 'ub', 'ub missing from xml for interval', int)
            return (lb, ub)
        else:
            raise UF.CHJError('Cost of ' + self.methodsum.get_name() + ' is not an interval cost')

    def get_model_comparison_value(self) -> int:
        if self.has_model_comparison_value():
            return UF.safe_get(self.xnode, 'modelvalue', 'modelvalue missing from xml', int)
        else:
            raise UF.CHJError(self.methodsum.get_name() + ' does not have a model comparison value')

    def __str__(self) -> str:
        if self.is_constant_cost():
            return str(self.get_constant_cost())
        if self.is_interval_cost():
            (lb,ub) = self.get_interval_cost()
            return '[' + str(lb) + ' ; ' + str(ub) + ']'
        return 'symbolic'

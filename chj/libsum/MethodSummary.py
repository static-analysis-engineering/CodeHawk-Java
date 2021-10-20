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

from chj.libsum.MethodSummarySignature import MethodSummarySignature
from chj.libsum.SummaryTimeCost import SummaryTimeCost

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chj.libsum.ClassSummary import ClassSummary
    import xml.etree.ElementTree as ET

import chj.util.fileutil as UF

class MethodSummary(object):

    def __init__(self, classsum: "ClassSummary", xnode: "ET.Element"):
        self.classsum = classsum
        self.xnode = xnode

    def is_valid(self) -> bool:
        return not ('valid' in self.xnode.attrib and self.xnode.get('valid') == 'no')

    def is_constructor(self) -> bool: return False

    def is_inherited(self) -> bool:
        return 'inherited' in self.xnode.attrib and self.xnode.get('inherited') == 'yes'

    def get_name(self) -> str: 
        return UF.safe_get(self.xnode, 'name', 'name missing from MethodSummary', str)

    def get_signature(self) -> MethodSummarySignature:
        return MethodSummarySignature(self, UF.safe_find(self.xnode, 'signature', 'signature missing from xml for methodsummary'))

    def has_time_cost(self) -> bool:
        return (not self.is_inherited()
                    and 'time-cost' in [ x.tag for x in UF.safe_find(self.xnode, 'summary', 'summary missing from xml for Method Summary')])

    def get_time_cost(self) -> SummaryTimeCost:
        if self.has_time_cost():
            errormsg = ' missing from xml for Method Summary'
            xsum = UF.safe_find(self.xnode, 'summary', 'summary ' + errormsg)
            xtim = UF.safe_find(xsum, 'time-cost', 'time-cost ' + errormsg)
            return SummaryTimeCost(self,xtim)
        else:
            raise UF.CHJError("Time Cost missing from xml for Method Summary")


class ConstructorSummary(MethodSummary):

    def __init__(self, classsum: "ClassSummary", xnode: "ET.Element"):
        MethodSummary.__init__(self,classsum,xnode)

    def is_constructor(self) -> bool: return True

    def is_inherited(self) -> bool: return False

    def get_name(self) -> str: return '<init>'

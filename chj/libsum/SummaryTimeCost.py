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


class SummaryTimeCost(object):

    def __init__(self,methodsum,xnode):
        self.methodsum = jmethodsum
        self.xnode = xnode

    def is_constant_cost(self):
        return len(self.xnode.find('cost')) > 0 and self.xnode.find('cost')[0].tag == 'cn'

    def is_interval_cost(self):
        xcost = self.xnode.find('cost')
        return 'lb' in xcost.attrib and 'ub' in xcost.attrib
            
    def is_from_model(self):
        return 'src' in self.xnode.attrib and self.xnode.get('src') == 'model'

    def has_model_comparison_value(self):
        return 'modelvalue' in self.xnode.attrib

    def has_calls(self):
        return 'calls' in self.xnode.attrib and self.xnode.get('calls') == 'yes'

    def get_constant_cost(self):
        return int(self.xnode.find('cost').find('cn').text)

    def get_interval_cost(self):
        if self.is_interval_cost():
            xcost = self.xnode.find('cost')
            return (int(xcost.get('lb')),int(xcost.get('ub')))

    def get_model_comparison_value(self):
        if self.has_model_comparison_value():
            return int(self.xnode.get('modelvalue'))

    def __str__(self):
        if self.is_constant_cost():
            return str(self.get_constant_cost())
        if self.is_interval_cost():
            (lb,ub) = self.get_interval_cost()
            return '[' + str(lb) + ' ; ' + str(ub) + ']'
        return 'symbolic'

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

class ExceptionHandlers():

    def __init__(self,app):
        self.app = app

    def as_dictionary(self):
        result = []
        table = {}
        def f(cmsix, m):
            if m.has_exception_table():
                result.append((cmsix,m.get_exception_table()))
        self.app.iter_methods(f)
        for (cmsix,t) in result:
            for ex in t.exceptionhandlers:
                aqname = str(self.app.jd.get_cms(cmsix).get_aqname())
                if not cmsix in table:
                    table[cmsix] = [ [ ex.startpc, ex.endpc, ex.handlerpc,
                                           ex.get_class_name().get_name(), aqname ] ]
                else:
                    table[cmsix].append([ ex.startpc, ex.endpc, ex.handlerpc,
                                              ex.get_class_name().get_name(), aqname ])
        return table

    def tostring(self):
        result = []
        lines = []
        def f(cmsix,m):
            if m.has_exception_table():
                result.append((cmsix,m.get_exception_table()))
        self.app.iter_methods(f)
        lines.append(' ')
        lines.append('start-pc  end-pc  handler-pc')
        for (cmsix,t) in result:
            lines.append(' ')
            lines.append(self.app.jd.get_cms(cmsix).get_aqname())
            lines.append(t.tostring())
        return '\n'.join(lines)

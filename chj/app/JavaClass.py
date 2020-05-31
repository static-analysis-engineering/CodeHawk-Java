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

from chj.app.BcDictionary import BcDictionary
from chj.app.Field import Field
from chj.app.JavaMethod import JavaMethod
from chj.app.ObjectSize import ObjectSize
from chj.userdata.UserDataClass import UserDataClass

class JavaClass():
    """Access point for class analysis results."""

    def __init__(self,app,xnode):
        self.app = app                      # AppAccess
        self.jd = self.app.jd               # DataDictionary
        self.fields = {}                    # cfsix -> Field
        self.methods = {}                   # cmsix -> JavaMethod
        self.cnix = int(xnode.get('ix'))
        self.package = self.jd.get_cn(self.cnix).get_package_name()
        self.superix = None
        self.bcd = None                     # BcDictionary
        self._initialize(xnode)

    def get_name(self): return self.jd.get_cn(self.cnix).get_simple_name()

    def get_qname(self): return self.jd.get_cn(self.cnix).get_qname()

    def get_aqname(self): return self.jd.get_cn(self.cnix).get_aqname()

    def has_super_class(self): return not (self.superix is None)

    def get_methods(self): return self.methods.values()

    def get_method(self,cmsix): return self.methods[cmsix]

    def iter_methods(self,f): 
        for cmsix in self.methods: f(cmsix,self.methods[cmsix])

    def get_loaded_strings(self,substring=None):
        results = []
        def f(cmsix,m): results.append((cmsix,m.get_loaded_strings(substring=substring)))
        self.iter_methods(f)
        return results

    def get_loaded_string_instructions(self,s):
        results = {}
        def f(m):
            instrs = m.get_loaded_string_instructions(s)
            if len(instrs) > 0: results[m.getid()] = instrs
        self.iter_methods(f)
        return results

    def get_static_initializers(self):
        results = []
        def f(cmsix,m):
            initializers = m.get_static_initializers()
            if len(initializers) > 0: results.append((cmsix,initializers))
        self.iter_methods(f)
        return results

    def get_static_field_readers(self):
        results = []
        def f(cmsix,m):
            readers = m.get_static_field_readers()
            if len(readers) > 0: results.append((cmsix,readers))
        self.iter_methods(f)
        return results

    def get_object_field_writers(self):
        results = []
        def f(cmsix,m):
            writers = m.get_object_field_writes()
            if len(writers) > 0: results.append((cmsix,writers))
        self.iter_methods(f)
        return results

    def get_object_field_readers(self):
        results = []
        def f(cmsix,m):
            readers = m.get_object_field_reads()
            if len(readers) > 0: results.append((cmsix,readers))
        self.iter_methods(f)
        return results

    def get_objects_created(self):
        results = []
        def f(cmsix,m):
            objectscreated = m.get_objects_created()
            if len(objectscreated) > 0: results.append((cmsix,objectscreated))
        self.iter_methods(f)
        return results

    def get_object_size(self):
        objsize = ObjectSize(self)
        for cfsix in self.fields:
            if self.fields[cfsix].isstatic: continue
            objsize.add_field(self.fields[cfsix].get_signature())
        if self.has_super_class():
            if self.jd.is_application_class(self.superix):
                sclass = self.app.get_class(self.superix)
                if not sclass is None:
                    objsize.add_object_size(sclass.get_object_size())
        return objsize

    def as_dictionary(self):
        result = {}
        for method in self.get_methods():
            methodresult = method.as_list()
            methodstring = method.get_method_signature_string() + " ( " + str(method.cmsix) + " ) "
            methodcmsix = str(method.cmsix)
            result[methodcmsix] = {}
            result[methodcmsix]['methodstring'] = methodstring
            result[methodcmsix]['result'] = methodresult
        return result 

    def _initialize(self,xnode):
        xdict = xnode.find('bcdictionary')
        if not xdict is None:
            self.bcd = BcDictionary(self,xdict)
        else:
            print('No dictionary found for ' + self.get_qname())
        for f in xnode.find('fields').findall('field'):
            self.fields[int(f.get('cfsix'))] = Field(self,f)
        for m in xnode.find('methods').findall('method'):
            if 'native' in m.attrib and m.get('native') == 'yes':
                continue
            self.methods[int(m.get('cmsix'))] = JavaMethod(self,m)
        if 'super-ix' in xnode.attrib:
            self.superix = int(xnode.get('super-ix'))



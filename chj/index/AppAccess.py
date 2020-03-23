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

from chj.app.JavaClass import JavaClass
from chj.cost.CostModel import CostModel

from chj.index.Callgraph import Callgraph
from chj.index.DataDictionary import DataDictionary

from chj.libsum.JDKModels import JDKModels
from chj.userdata.UserDataClass import UserDataClass

class AppAccess(object):

    def __init__(self,path):
        self.path = path
        self.jdkmodels = JDKModels(self)
        self.jd = DataDictionary(self)
        self.callgraph = None                # JDCallgraph
        self.classes = {}                    # cnix -> JavaClass (application classes)
        self.userdataclasses = {}            # cnix -> UserDataClass
        self.costmodel = None                # JCostModel
        self.classesloaded = False

    def iter_classes(self,f):
        self._get_classes()
        for cnix in self.classes: f(self.classes[cnix])

    def iter_user_classes(self,f):
        self._get_userdata_classes()
        for cnix in self.userdataclasses: f(self.userdataclasses[cnix])

    def get_class(self,cnix):
        '''returns a JavaClass object (available for application classes only)'''
        self._get_class(cnix)
        if cnix in self.classes: return self.classes[cnix]

    def get_classes(self):
        self._get_classes()
        return self.classes

    def get_methods(self):
        '''returns list of JavaMethod objects (application methods only)'''
        result = []
        def domethod(cmsix,m): result.append((cmsix,m))
        def doclass(c): c.iter_methods(domethod)
        self.iter_classes(doclass)
        return result

    def iter_methods(self,f):
        '''iterates over application methods'''
        for (cmsix,m) in self.get_methods(): f(cmsix,m)

    def get_method(self,cmsix):
        '''returns a JavaMethod object (available for application methods only)'''
        cnix = self.jd.get_cms(cmsix).classname.index
        return self.get_class(cnix).get_method(cmsix)

    def get_method_as_dictionary(self, cmsix):
        cnix = self.jd.get_cms(cmsix).classname.index
        return self.get_class(cnsix).get_method_as_dictionary(dmsix)

    def has_user_data_class(self,cnix):
        self._get_userdata_classes()
        return cnix in self.userdataclasses

    def get_user_data_class(self,cnix):
        self._get_userdata_classes()
        if cnix in self.userdataclasses:
            return  self.userdataclasses[cnix]

    def get_callgraph(self):
        '''returns a Callgraph object'''
        self._get_callgraph()
        return self.callgraph

    def get_costmodel(self):
        '''returns a CostModel object'''
        self._get_costmodel()
        return self.costmodel

    def get_loaded_strings(self):
        results = []
        def f(c): results.extend(c.get_loaded_strings())
        self.iter_classes(f)
        return results

    def get_loaded_string_instructions(self):
        results = {}
        def f(c):
            strings = c.get_loaded_string_instructions(s)
            if len(strings) > 0: results[c.getid()] = strings
        self.iter_classes(f)
        return results

    def get_static_initializers(self):
        results = []
        def f(c):
            initializers = c.get_static_initializers()
            if len(initializers) > 0: results.extend(initializers)
        self.iter_classes(f)
        return results

    def get_static_field_readers(self):
        results = []
        def f(c):
            readers = c.get_static_field_readers()
            if len(readers) > 0: results.extend(readers)
        self.iter_classes(f)
        return results

    def get_object_field_writers(self):
        results = []
        def f(c):
            writers = c.get_object_field_writers()
            if len (writers) > 0: results.extend(writers)
        self.iter_classes(f)
        return results

    def get_object_field_readers(self):
        results = []
        def f(c):
            readers = c.get_object_field_readers()
            if len (readers) > 0: results.extend(readers)
        self.iter_classes(f)
        return results

    def get_objects_created(self):
        results = []
        def f(c):
            objectscreated = c.get_objects_created()
            if len (objectscreated) > 0: results.extend(objectscreated)
        self.iter_classes(f)
        return results

    def _get_class(self,cnix):
        if cnix in self.classes: return
        cn = self.jd.get_cn(cnix)
        if not cn is None:
            xnode = UF.get_app_class_xnode(self.path,cn.get_package_name(),
                                                    cn.get_simple_name())
            if xnode is None:
                print('Error in loading class file ' + str(cn))
                exit(1)
            self.classes[cnix] = JavaClass(self,xnode)
        
    def _get_classes(self):
        if self.classesloaded: return
        for (cname,cnix) in self.jd.appclassindices.items():
            if cnix in self.classes: continue
            cn = self.jd.get_cn(cnix)
            xnode = UF.get_app_class_xnode(self.path,cn.get_package_name(),cn.get_simple_name())
            if xnode is None:
                print('Unable to load ' + cn.get_name())
                continue
            self.classes[cnix] = JavaClass(self,xnode)
            self.classesloaded = True

    def _get_userdata_classes(self):
        for (cname,cnix) in self.jd.appclassindices.items():
            if cnix in self.userdataclasses: continue
            cn = self.jd.get_cn(cnix)
            xnode = UF.get_userdataclass_xnode(self.path,cn.get_package_name(),cn.get_simple_name())
            if not xnode is None:
                self.userdataclasses[cnix] = UserDataClass(self,xnode)

    def _get_costmodel(self):
        if self.costmodel is None:
            self.costmodel = CostModel(self)

    def _get_callgraph(self):
        if self.callgraph is None:
            xcg = UF.get_datacallgraph_xnode(self.path)
            if not xcg is None:
                self.callgraph = Callgraph(self,xcg)
            else:
                print('Call graph not found')
                


        



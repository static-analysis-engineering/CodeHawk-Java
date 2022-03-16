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

import chj.util.fileutil as UF

from chj.app.JavaClass import JavaClass
from chj.cost.CostModel import CostModel
from chj.index.Callgraph import Callgraph
from chj.index.DataDictionary import DataDictionary
from chj.libsum.JDKModels import JDKModels
from chj.userdata.UserDataClass import UserDataClass
from typing import cast, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.Instruction import Instruction
    from chj.app.JavaMethod import JavaMethod
    from chj.index.Classname import Classname
    from chj.index.FieldSignature import FieldSignature

class AppAccess(object):

    def __init__(self, path:str) -> None:
        self.path = path
        self.jdkmodels = JDKModels(self)
        self.jd = DataDictionary(self)
        self.callgraph: Optional[Callgraph] = None              # Callgraph
        self.classes: Dict[int, JavaClass] = {}                 # cnix -> JavaClass (application classes)
        self.userdataclasses: Dict[int, UserDataClass] = {}     # cnix -> UserDataClass
        self.costmodel: Optional[CostModel] = None              # CostModel
        self.classesloaded = False

    def iter_classes(self, f:Callable[[JavaClass], None]) -> None:
        self._get_classes()
        for cnix in self.classes: f(self.classes[cnix])

    def iter_user_classes(self, f: Callable[[UserDataClass], None]) -> None:
        self._get_userdata_classes()
        for cnix in self.userdataclasses: f(self.userdataclasses[cnix])

    def get_class(self, cnix: int) -> JavaClass:
        '''returns a JavaClass object (available for application classes only)'''
        self._get_class(cnix)
        if cnix in self.classes:
            return self.classes[cnix]
        else:
            raise UF.CHJError('cnix: ' + str(cnix) + ' is not an application class')

    def get_classes(self) -> Dict[int, JavaClass]:
        self._get_classes()
        return self.classes

    def get_methods(self) -> List[Tuple[int, "JavaMethod"]]:
        '''returns list of JavaMethod objects (application methods only)'''
        result = []
        def domethod(cmsix: int, m: "JavaMethod") -> None:
            result.append((cmsix,m))
        def doclass(c: JavaClass) -> None:
            c.iter_methods(domethod)
        self.iter_classes(doclass)
        return result

    def iter_methods(self, f: Callable[[int, "JavaMethod"], None]) -> None:
        '''iterates over application methods'''
        for (cmsix,m) in self.get_methods(): f(cmsix,m)

    def get_method(self, cmsix: int) -> "JavaMethod":
        '''returns a JavaMethod object (available for application methods only)'''
        cnix = self.jd.get_cms(cmsix).classname.index
        return self.get_class(cnix).get_method(cmsix)

    def get_method_as_dictionary(self, cmsix: int) -> Dict[str, str]:
        cnix = self.jd.get_cms(cmsix).classname.index
        return self.get_class(cnix).get_method(cmsix).as_dictionary()

    def has_user_data_class(self, cnix: int) -> bool:
        self._get_userdata_classes()
        return cnix in self.userdataclasses

    def get_user_data_class(self, cnix: int) -> UserDataClass:
        self._get_userdata_classes()
        if cnix in self.userdataclasses:
            return self.userdataclasses[cnix]
        else:
            raise UF.CHJError('UserDataClass: ' + str(cnix) + ' missing from xml')

    def get_callgraph(self) -> Callgraph:
        '''returns a Callgraph object'''
        self._get_callgraph()
        return cast(Callgraph, self.callgraph)

    def get_costmodel(self) -> CostModel:
        '''returns a CostModel object'''
        self._get_costmodel()
        return cast(CostModel, self.costmodel)

    def get_loaded_strings(self, substring: str=None) -> List[Tuple[int, List[Tuple[int, str]]]]:
        results = []
        def f(c: JavaClass) -> None: results.extend(c.get_loaded_strings(substring=substring))
        self.iter_classes(f)
        return results

    def get_loaded_string_instructions(self) -> Dict[int, Dict[int, List["Instruction"]]]:
        results: Dict[int, Dict[int, List["Instruction"]]] = {}
        def f(c: JavaClass) -> None:
            strings = c.get_loaded_string_instructions()
            if len(strings) > 0: results[c.cnix] = strings
        self.iter_classes(f)
        return results

    def get_static_initializers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(c: JavaClass) -> None:
            initializers = c.get_static_initializers()
            if len(initializers) > 0: results.extend(initializers)
        self.iter_classes(f)
        return results

    def get_static_field_readers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(c: JavaClass) -> None:
            readers = c.get_static_field_readers()
            if len(readers) > 0: results.extend(readers)
        self.iter_classes(f)
        return results

    def get_object_field_writers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(c: JavaClass) -> None:
            writers = c.get_object_field_writers()
            if len (writers) > 0: results.extend(writers)
        self.iter_classes(f)
        return results

    def get_object_field_readers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(c: JavaClass) -> None:
            readers = c.get_object_field_readers()
            if len (readers) > 0: results.extend(readers)
        self.iter_classes(f)
        return results

    def get_objects_created(self) -> List[Tuple[int, List[Tuple[int, "Instruction"]]]]:
        results = []
        def f(c: JavaClass) -> None:
            objectscreated = c.get_objects_created()
            if len (objectscreated) > 0: results.extend(objectscreated)
        self.iter_classes(f)
        return results

    def _get_class(self, cnix: int) -> None:
        if cnix in self.classes: return
        cn = self.jd.get_cn(cnix)
        if not cn is None:
            xnode = UF.get_app_class_xnode(self.path,cn.get_package_name(),
                                                    cn.get_simple_name())
            if xnode is None:
                print('Error in loading class file ' + str(cn))
                exit(1)
            self.classes[cnix] = JavaClass(self,xnode)
        
    def _get_classes(self) -> None:
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

    def _get_userdata_classes(self) -> None:
        for (cname,cnix) in self.jd.appclassindices.items():
            if cnix in self.userdataclasses: continue
            cn = self.jd.get_cn(cnix)
            xnode = UF.get_userdataclass_xnode(self.path,cn.get_package_name(),cn.get_simple_name())
            if not xnode is None:
                self.userdataclasses[cnix] = UserDataClass(self,xnode)

    def _get_costmodel(self) -> None:
        if self.costmodel is None:
            self.costmodel = CostModel(self)

    def _get_callgraph(self) -> None:
        if self.callgraph is None:
            xcg = UF.get_datacallgraph_xnode(self.path)
            if not xcg is None:
                self.callgraph = Callgraph(self,xcg)
            else:
                raise UF.CHJError('Call graph not found in xml')
                


        



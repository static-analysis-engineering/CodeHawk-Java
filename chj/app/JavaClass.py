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

import chj.util.fileutil as UF

from typing import Any, cast, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import ValuesView
    from chj.app.Instruction import Instruction
    from chj.index.AppAccess import AppAccess
    from chj.index.Classname import Classname
    from chj.index.DataDictionary import DataDictionary
    from chj.index.FieldSignature import FieldSignature
    import xml.etree.ElementTree as ET

class JavaClass():
    """Access point for class analysis results."""

    def __init__(self, app: "AppAccess", xnode:"ET.Element"):
        self.app = app                              # AppAccess
        self.jd: "DataDictionary" = self.app.jd     # DataDictionary
        self.fields: Dict[int, Field] = {}          # cfsix -> Field
        self.methods: Dict[int, JavaMethod] = {}    # cmsix -> JavaMethod
        self.cnix = UF.safe_get(xnode, 'ix' , 'cnix missing from xml', int)
        self.package: str = self.jd.get_cn(self.cnix).get_package_name()
        self.superix: Optional[int] = None
        self.bcd: Optional[BcDictionary] = None     # BcDictionary
        self._initialize(xnode)

    def get_name(self) -> str: return self.jd.get_cn(self.cnix).get_simple_name()

    def get_qname(self) -> str: return self.jd.get_cn(self.cnix).get_qname()

    def get_aqname(self) -> str: return self.jd.get_cn(self.cnix).get_aqname()

    def has_super_class(self) -> bool: return not (self.superix is None)

    def get_methods(self) -> "ValuesView[JavaMethod]": return self.methods.values()

    def get_method(self, cmsix: int) -> JavaMethod: return self.methods[cmsix]

    def iter_methods(self, f: Callable[[int, JavaMethod], None]) -> None:
        for cmsix in self.methods: f(cmsix,self.methods[cmsix])

    def get_loaded_strings(self, substring: str=None) -> List[Tuple[int, List[Tuple[int, str]]]]:
        results = []
        def f(cmsix: int, m: JavaMethod) -> None:
            results.append((cmsix,m.get_loaded_strings(substring=substring)))
        self.iter_methods(f)
        return results

    def get_loaded_string_instructions(self) -> Dict[int, List["Instruction"]]:
        results = {}
        def f(_:int, m: JavaMethod) -> None:
            instrs = m.get_loaded_string_instructions()
            if len(instrs) > 0: results[m.cmsix] = instrs
        self.iter_methods(f)
        return results

    def get_static_initializers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(cmsix: int, m: JavaMethod) -> None:
            initializers = m.get_static_initializers()
            if len(initializers) > 0: results.append((cmsix,initializers))
        self.iter_methods(f)
        return results

    def get_static_field_readers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(cmsix: int, m: JavaMethod) -> None:
            readers = m.get_static_field_readers()
            if len(readers) > 0: results.append((cmsix,readers))
        self.iter_methods(f)
        return results

    def get_object_field_writers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(cmsix: int, m: JavaMethod) -> None:
            writers = m.get_object_field_writes()
            if len(writers) > 0: results.append((cmsix,writers))
        self.iter_methods(f)
        return results

    def get_object_field_readers(self) -> List[Tuple[int, List[Tuple[int, "Classname", "FieldSignature"]]]]:
        results = []
        def f(cmsix: int, m: JavaMethod) -> None:
            readers = m.get_object_field_reads()
            if len(readers) > 0: results.append((cmsix,readers))
        self.iter_methods(f)
        return results

    def get_objects_created(self) -> List[Tuple[int, List[Tuple[int, "Instruction"]]]]:
        results = []
        def f(cmsix: int, m: JavaMethod) -> None:
            objectscreated = m.get_objects_created()
            if len(objectscreated) > 0: results.append((cmsix,objectscreated))
        self.iter_methods(f)
        return results

    def get_object_size(self) -> ObjectSize:
        objsize = ObjectSize(self)
        for cfsix in self.fields:
            if self.fields[cfsix].isstatic: continue
            objsize.add_field(self.fields[cfsix].get_signature())
        if self.has_super_class():
            superix = cast(int, self.superix)
            if self.jd.is_application_class(superix):
                sclass = self.app.get_class(superix)
                if not sclass is None:
                    objsize.add_object_size(sclass.get_object_size())
        return objsize

    def as_dictionary(self) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        for method in self.get_methods():
            methodresult = method.as_list()
            methodstring = method.get_method_signature_string() + " ( " + str(method.cmsix) + " ) "
            methodcmsix = str(method.cmsix)
            result[methodcmsix] = {}
            result[methodcmsix]['methodstring'] = methodstring
            result[methodcmsix]['result'] = methodresult
        return result 

    def _initialize(self, xnode: "ET.Element") -> None:
        xdict = xnode.find('bcdictionary')
        if not xdict is None:
            self.bcd = BcDictionary(self,xdict)
        else:
            print('No dictionary found for ' + self.get_qname())

        errormsg = ' missing from xml for ' + self.get_qname()
        for f in UF.safe_find(xnode, 'fields', 'fields' + errormsg).findall('field'):
            self.fields[UF.safe_get(f, 'cfsix', 'cfsix' + errormsg ,int)] = Field(self,f)
        for m in UF.safe_find(xnode, 'methods', 'methods' + errormsg).findall('method'):
            if 'native' in m.attrib and m.get('native') == 'yes':
                continue
            self.methods[UF.safe_get(m, 'cmsix', 'cmsix' + errormsg, int)] = JavaMethod(self,m)
        if 'super-ix' in xnode.attrib:
            self.superix = UF.safe_get(xnode, 'super-ix', 'super-ix' + errormsg, int)



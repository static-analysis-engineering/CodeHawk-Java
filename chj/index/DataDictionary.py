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

from chj.index.JTypeDictionary import JTypeDictionary
from chj.index.TaintDictionary import TaintDictionary
from chj.index.CallgraphDictionary import CallgraphDictionary
from chj.index.JTermDictionary import JTermDictionary

from typing import Callable, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.index.CallgraphDictionary import CallgraphTargetBase
    from chj.index.Classname import Classname
    from chj.index.FieldSignature import FieldSignature
    from chj.index.FieldSignature import ClassFieldSignature
    from chj.index.MethodSignature import MethodSignature
    from chj.index.MethodSignature import ClassMethodSignature
    import chj.index.Taint as T

    TORIGIN_CONSTRUCTOR_TYPE = Union[T.VariableTaint,
                                    T.FieldTaint,
                                    T.CallerTaint,
                                    T.TopTargetTaint,
                                    T.StubTaint]


class DataDictionary():

    def __init__(self, app: "AppAccess") -> None:
        self.app = app                                                  # AppAccess
        self.tpd: JTypeDictionary                                       # JTypeDictionary
        self.ttd: Optional[TaintDictionary] = None                      # TaintDictionary
        self.cgd: CallgraphDictionary                                   # CallgraphDictionary
        self.jtd: JTermDictionary                                       # JTermDictionary
        self.appclassindices: Dict[str, int] = {}                       # classname (string) -> cnix
        self.msindices: Dict[Tuple[str, str], int] = {}                 # (name(string),sig(string)) -> msix
        self.mssignatures: Dict[int, Tuple[str, str]] = {}              # msix -> (name(string),sig(string))
        self.mstargets: Dict[int, Tuple[List[int], List[int], List[int]]] = {}            # msix -> (stub-cnix list, appclass-cnix list, native-cnix list)
        self.callgraphedges: Dict[Tuple[int, int], 
                              Tuple[int, "CallgraphTargetBase"]] = {}     # (cmsix,pc) -> (msix,Calltarget)
        self.missingclasses: List[int] = []                             # list of cnix
        self._initialize()

    def get_cn(self, cnix: int) -> "Classname":
        return self.tpd.get_class_name(cnix)

    def get_fs(self, fsix: int) -> "FieldSignature":
        return self.tpd.get_field_signature_data(fsix)

    def get_cfs(self, cfsix: int) -> "ClassFieldSignature":
        return self.tpd.get_class_field_signature_data(cfsix)

    def get_ms(self, msix: int) -> "MethodSignature":
        return self.tpd.get_method_signature_data(msix)

    def get_cms(self, cmsix: int) -> "ClassMethodSignature":
        return self.tpd.get_class_method_signature_data(cmsix)

    def get_msix(self, msname: str, msstring: str) -> int:
        if (msname,msstring) in self.msindices:
            return self.msindices[(msname,msstring)]
        else:
            raise UF.CHJError(msname + ', ' + msstring + ' missing from msindices.')

    def get_cnix(self, classname: str) -> int:
        if classname in self.appclassindices:
            return self.appclassindices[classname]
        else:
            raise UF.CHJError(classname + ' missing from appclassindices.')

    def get_cmsix(self, cnix:int, msix:int) -> int:
        return self.tpd.get_cms_index([],[cnix,msix])

    def iter_appclasses(self, f:Callable[[int], None]) -> None:
        '''iterates over the indices of application class names'''
        for c in sorted(self.appclassindices): f(self.appclassindices[c])

    def iter_fields(self, f:Callable[["ClassFieldSignature"], None]) -> None:
        '''iterates over class field signatures of application classes'''
        cnindices = self.appclassindices.values()
        for fld in self.tpd.get_fields():
            if fld.cnix in cnindices: f(fld)

    def iter_methods(self, f:Callable[["ClassMethodSignature"], None]) -> None:
        '''iterates over class method signatures of application classes'''
        cnindices = self.appclassindices.values()
        for m in sorted(self.tpd.get_methods()):
            if m.cnix in cnindices: f(m)

    def iter_method_signature_targets(self,f: Callable[[int, Tuple[List[int], List[int], List[int]]], None]) -> None:
        for (msix,tgts) in self.mstargets.items(): f(msix,tgts)

    def iter_taint_origins(self, f: Callable[["TORIGIN_CONSTRUCTOR_TYPE"], None]) -> None:
        if self.ttd != None:
            taintorigins = self.ttd.get_taint_origins()
            for m in self.ttd.get_taint_origins(): f(m)
        else:
            print('Taint Dictionary not found!')

    #def get_stub(self, cnix: int): 
    #    return self.app.jdkmodels.getstub(cnix)

    def iter_method_signatures(self, f: Callable[[Tuple[str, str]], None]) -> None:
        for m in self.mssignatures: f(self.mssignatures[m])

    def get_method_signatures(self, name: str) -> Dict[int, str]:
        result = {}
        for (msix,(msname,mssig)) in self.mssignatures.items():
            if msname == name:
                result[msix] = mssig
        return result

    def get_implementing_classes(self, msix: int) -> Optional[List[int]]:
        if msix in self.mstargets:
            (stubs,app,natives) = self.mstargets[msix]
            return stubs + app + natives
        else:
            return None

    def iter_callgraph_edges(self, f: Callable[[int, int, int, "CallgraphTargetBase"], None]) -> None:
        '''iterates over callgraph edges with arguments: caller cmsix, pc, callee msix, targets'''
        for (cmsix,pc) in self.callgraphedges:
            (msix,tgt) = self.callgraphedges[ (cmsix,pc) ]
            f(cmsix,pc,msix,tgt)

    def is_application_class(self, cnix: int) -> bool: return cnix in self.appclassindices.values()

    def has_call_target(self, cmsix: int, pc: int) -> bool: return (cmsix,pc) in self.callgraphedges

    def get_call_target(self, cmsix: int, pc: int) -> Tuple[int, "CallgraphTargetBase"]:
        if self.has_call_target(cmsix,pc): 
            return self.callgraphedges[(cmsix,pc)]
        else:
            raise UF.CHJError('Call target at cmsix: ' + str(cmsix) + ', pc: ' + str(pc) + ' missing')

    def targets_to_string(self) -> str:
        '''return a list of method signatures and their implementations/stubs.'''
        lines = []
        for msix in sorted(self.mstargets,key=lambda x:self.mssignatures[x]):
            lines.append(' ')
            lines.append(str(self.tpd.get_method_signature_data(msix)))
            for t in self.mstargets[msix][0]:
                lines.append('  ' + str(self.get_cn(t)))
        return '\n'.join(lines)

    def _initialize(self) -> None:
        path = self.app.path
        self._initialize_type_dictionary(path)
        self._initialize_jterm_dictionary(path)
        self._initialize_taint_dictionary(path)
        self._initialize_app_classes(path)
        self._initialize_missing_classes(path)
        self._initialize_method_signatures(path)
        self._initialize_callgraph(path)

    def _initialize_type_dictionary(self, path: str) -> None:
        xdict = UF.get_datadictionary_xnode(path)
        if not xdict is None:
            self.tpd = JTypeDictionary(self,UF.safe_find(xdict, 'type-dictionary', 'type-dictionary missing from xml'))

    def _initialize_jterm_dictionary(self, path: str) -> None:
        xnode = UF.get_jterm_dictionary_xnode(path)
        if not xnode is None:
            self.jtd = JTermDictionary(self,UF.safe_find(xnode, 'jterm-dictionary', 'jterm-dictionary missing from xml'))

    def _initialize_taint_dictionary(self, path: str) -> None:
        xnode = UF.get_data_taint_origins_xnode(path)
        if not xnode is None:
            self.ttd = TaintDictionary(self,UF.safe_find(xnode, 'taint-dictionary', 'taint-dictionary missing from xml'))

    def _initialize_callgraph(self, path: str) -> None:
        xnode = UF.get_datacallgraph_xnode(path)
        if not xnode is None:
            self.cgd = CallgraphDictionary(self,UF.safe_find(xnode, 'dictionary', 'callgraph dictionary missing from xml'))
            xedges = UF.safe_find(xnode, 'edges', 'edges missing from xml')
            for xedge in xedges.findall('edge'):
                cmsix = UF.safe_get(xedge, 'ix', 'cmsix missing from xml', int)
                pc = UF.safe_get(xedge, 'pc', 'pc missing from xml', int)
                msix = UF.safe_get(xedge, 'ms-ix', 'ms-ix missing from xml', int)
                tgt = self.cgd.read_xml_target(xedge)
                self.callgraphedges[(cmsix,pc)] = (msix,tgt)
                
    def _initialize_app_classes(self, path: str) -> None:
        xnode = UF.get_dataclassnames_xnode(path)
        if not xnode is None:
            for cn in xnode.findall('cn'):
                if "package" in cn.attrib and len(UF.safe_get(cn, 'package', 'packing missing from xml', str)) > 0:
                    cname = UF.safe_get(cn, 'package', 'package missing from xml', str) \
                            + '.' + UF.safe_get(cn, 'name', 'name of class missing from ' + path + ' xml.', str)
                else:
                    cname = UF.safe_get(cn, 'name', 'name of class missing from ' + path + ' xml.', str)
                self.appclassindices[cname] = UF.safe_get(cn, 'ix', 'ix of class missing from ' + path + ' xml.', int)

    def _initialize_missing_classes(self, path: str) -> None:
        xnode = UF.get_datamissingitems_xnode(path)
        if not xnode is None:
            xmissing = UF.safe_find(xnode, 'missing-classes' ,'missing-classes missing from xml')
            for cn in xmissing.findall('cn'):
                self.missingclasses.append(UF.safe_get(cn, 'ix', 'ix missing from xml', int))

    def _initialize_method_signatures(self,path: str) -> None:
        xnode = UF.get_datasignatures_xnode(path)
        if not xnode is None:
            for xms in xnode.findall('ms'):
                msix = UF.safe_get(xms, 'ix', 'ix missing from xml', int)
                msname = UF.safe_get(xms, 'name', 'name missing from xml', str)
                mssig = UF.safe_get(xms, 'sig', 'sig missing from xml', str)
                xstubs = xms.findall('stubs')
                stubs = []
                if len(xstubs) > 0:
                    for xstub in xstubs:
                        if 'ixs' in xstub.attrib:
                            stubs += [ int(x) for x in UF.safe_get(xstub, 'ixs', 'ixs missing from xml', str).split(',') ]
                appmethods = []
                xbcs = xms.findall('bc')
                if len(xbcs) > 0:
                    for xbc in xbcs:
                        if 'ixs' in xbc.attrib:
                            appmethods += [ int(x) for x in UF.safe_get(xbc, 'ixs', 'ixs missing from xml', str).split(',') ]
                natives = []
                xnatives = xms.findall('native')
                if len(xnatives) > 0:
                    for xnative in xnatives:
                        if 'ixs' in xnative.attrib:
                            natives += [ int(x) for x in UF.safe_get(xnative, 'ixs', 'ixs missing from xml', str).split(',') ]
                self.msindices[(msname,mssig)] = msix
                self.mssignatures[msix] = (msname,mssig)
                self.mstargets[msix] = (stubs,appmethods,natives)
                


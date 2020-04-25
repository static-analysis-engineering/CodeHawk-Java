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

class DataDictionary():

    def __init__(self,app):
        self.app = app                  # AppAccess
        self.tpd = None                 # JTypeDictionary
        self.ttd = None                 # TaintDictionary
        self.cgd = None                 # CallgraphDictionary
        self.jtd = None                 # JTermDictionary
        self.appclassindices = {}       # classname (string) -> cnix
        self.msindices = {}             # (name(string),sig(string)) -> msix
        self.mssignatures = {}          # msix -> (name(string),sig(string))
        self.mstargets = {}             # msix -> (stub-cnix list, appclass-cnix list, native-cnix list)
        self.callgraphedges = {}        # (cmsix,pc) -> (msix,Calltarget)
        self.missingclasses = []        # list of cnix
        self._initialize()

    def get_cn(self,cnix): return self.tpd.get_class_name(cnix)

    def get_fs(self,fsix): return self.tpd.get_field_signature_data(fsix)

    def get_cfs(self,cfsix): return self.tpd.get_class_field_signature_data(cfsix)

    def get_ms(self,msix): return self.tpd.get_method_signature_data(msix)

    def get_cms(self,cmsix): return self.tpd.get_class_method_signature_data(cmsix)

    def get_msix(self,msname,msstring):
        if (msname,msstring) in self.msindices:
            return self.msindices[(msname,msstring)]

    def get_cnix(self,classname):
        if classname in self.appclassindices:
            return self.appclassindices[classname]

    def get_cmsix(self,cnix,msix):
        return self.tpd.get_cms_index([],[cnix,msix])

    def iter_appclasses(self,f):
        '''iterates over the indices of application class names'''
        for c in sorted(self.appclassindices): f(self.appclassindices[c])

    def iter_fields(self,f):
        '''iterates over class field signatures of application classes'''
        cnindices = self.appclassindices.values()
        for fld in sorted(self.tpd.get_fields()):
            if fld.cnix in cnindices: f(fld)

    def iter_methods(self,f):
        '''iterates over class method signatures of application classes'''
        cnindices = self.appclassindices.values()
        for m in sorted(self.tpd.get_methods()):
            if m.cnix in cnindices: f(m)

    def iter_method_signature_targets(self,f):
        for (msix,tgts) in self.mstargets.items(): f(msix,tgts)

    def iter_taint_origins(self,f):
        if self.ttd != None:
            taintorigins = self.ttd.get_taint_origins()
            for m in self.ttd.get_taint_origins(): f(m)
        else:
            print('Taint Dictionary not found!')

    def get_stub(self,cnix): return self.app.get_jdk_models.getstub(cnix)

    def iter_method_signatures(self,f):
        for m in self.mssignatures: f(self.mssignatures[m])

    def get_method_signatures(self,name):
        result = {}
        for (msix,(msname,mssig)) in self.mssignatures.items():
            if msname == name:
                result[msix] = mssig
        return result

    def get_implementing_classes(self,msix):
        if msix in self.mstargets:
            (stubs,app,natives) = self.mstargets[msix]
            return stubs + app + natives
        else:
            return []

    def iter_callgraph_edges(self,f):
        '''iterates over callgraph edges with arguments: caller cmsix, pc, callee msix, targets'''
        for (cmsix,pc) in self.callgraphedges:
            (msix,tgt) = self.callgraphedges[ (cmsix,pc) ]
            f(cmsix,pc,msix,tgt)

    def is_application_class(self,cnix): return cnix in self.appclassindices.values()

    def has_call_target(self,cmsix,pc): return (cmsix,pc) in self.callgraphedges

    def get_call_target(self,cmsix,pc):
        if self.has_call_target(cmsix,pc): return self.callgraphedges[(cmsix,pc)]

    def targets_to_string(self):
        '''return a list of method signatures and their implementations/stubs.'''
        lines = []
        for msix in sorted(self.mstargets,key=lambda x:self.mssignatures[x]):
            lines.append(' ')
            lines.append(str(self.tpd.get_method_signature_data(msix)))
            for t in self.mstargets[msix][0]:
                lines.append('  ' + str(self.get_cn(t)))
        return '\n'.join(lines)

    def _initialize(self):
        path = self.app.path
        self._initialize_type_dictionary(path)
        self._initialize_jterm_dictionary(path)
        self._initialize_taint_dictionary(path)
        self._initialize_app_classes(path)
        self._initialize_missing_classes(path)
        self._initialize_method_signatures(path)
        self._initialize_callgraph(path)

    def _initialize_type_dictionary(self,path):
        xdict = UF.get_datadictionary_xnode(path)
        if not xdict is None:
            self.tpd = JTypeDictionary(self,xdict.find('type-dictionary'))

    def _initialize_jterm_dictionary(self,path):
        xnode = UF.get_jterm_dictionary_xnode(path)
        if not xnode is None:
            self.jtd = JTermDictionary(self,xnode.find('jterm-dictionary'))

    def _initialize_taint_dictionary(self,path):
        xnode = UF.get_data_taint_origins_xnode(path)
        if not xnode is None:
            self.ttd = TaintDictionary(self,xnode.find('taint-dictionary'))

    def _initialize_callgraph(self,path):
        xnode = UF.get_datacallgraph_xnode(path)
        if not xnode is None:
            self.cgd = CallgraphDictionary(self,xnode.find('dictionary'))
            for xedge in xnode.find('edges').findall('edge'):
                cmsix = int(xedge.get('ix'))
                pc = int(xedge.get('pc'))
                msix = int(xedge.get('ms-ix'))
                tgt = self.cgd.read_xml_target(xedge)
                self.callgraphedges[(cmsix,pc)] = (msix,tgt)
                
    def _initialize_app_classes(self,path):
        xnode = UF.get_dataclassnames_xnode(path)
        if not xnode is None:
            for cn in xnode.findall('cn'):
                if "package" in cn.attrib and len(cn.get('package')) > 0:
                    cname = cn.get('package') + '.' + cn.get('name')
                else:
                    cname = cn.get('name')
                self.appclassindices[cname] = int(cn.get('ix'))

    def _initialize_missing_classes(self,path):
        xnode = UF.get_datamissingitems_xnode(path)
        if not xnode is None:
            for cn in xnode.find('missing-classes').findall('cn'):
                self.missingclasses.append(int(cn.get('ix')))

    def _initialize_method_signatures(self,path):
        xnode = UF.get_datasignatures_xnode(path)
        if not xnode is None:
            for xms in xnode.findall('ms'):
                msix = int(xms.get('ix'))
                msname = xms.get('name')
                mssig = xms.get('sig')
                xstubs = xms.findall('stubs')
                stubs = []
                if len(xstubs) > 0:
                    for xstub in xstubs:
                        if 'ixs' in xstub.attrib:
                            stubs += [ int(x) for x in xstub.get('ixs').split(',') ]
                appmethods = []
                xbcs = xms.findall('bc')
                if len(xbcs) > 0:
                    for xbc in xbcs:
                        if 'ixs' in xbc.attrib:
                            appmethods += [ int(x) for x in xbc.get('ixs').split(',') ]
                natives = []
                xnatives = xms.findall('native')
                if len(xnatives) > 0:
                    for xnative in xnatives:
                        if 'ixs' in xnative.attrib:
                            natives += [ int(x) for x in xnative.get('ixs').split(',') ]
                self.msindices[(msname,mssig)] = msix
                self.mssignatures[msix] = (msname,mssig)
                self.mstargets[msix] = (stubs,appmethods,natives)
                


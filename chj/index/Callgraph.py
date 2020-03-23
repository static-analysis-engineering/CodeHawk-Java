# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma and Andrew McGraw
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

from chj.util.DotGraph import DotGraph

class Callgraph():

    def __init__(self,app,xnode):
        self.app = app                   # AppAccess
        self.jd = self.app.jd            # DataDictionary
        self.cgd = self.jd.cgd           # CallgraphDictionary
        self.xnode = xnode
        self.edges = {}             # cms-ix -> pc -> CallgraphTargetBase
        self.callbackedges = []     # cms-ix list
        self._get_edges()

    def as_dot(self, cmsix):
        dotgraph = DotGraph("cg_" + str(cmsix))
        dotgraph.add_node(self.app.get_method(cmsix).get_aqname()) 

        rem_nodes = [ cmsix ]
        done_nodes = []

        while len(rem_nodes) > 0:
            cmsix = rem_nodes.pop()
            done_nodes.append(cmsix)
            methodname = self.app.get_method(cmsix).get_aqname()

            tgts = self._get_method_edges(cmsix)

            for pc in tgts:
                (msix, tgt) = tgts[pc]
                for cnix in tgt.cnixs:
                    tgtcmsix = self.jd.get_cmsix(cnix, msix)
                    tgtname = (self.app.get_method(tgtcmsix).get_aqname() if 
                            self.jd.is_application_class(cnix) else 
                            self.jd.get_cn(cnix).get_name() + '.' + self.jd.mssignatures[msix][0])
                    dotgraph.add_edge(methodname, tgtname)
                    if self.jd.is_application_class(cnix):
                        if tgtcmsix not in done_nodes: rem_nodes.append(tgtcmsix)
        return dotgraph

    def as_rev_dot(self, cmsix):
        dotgraph = DotGraph("revcg_" + str(cmsix))
        dotgraph.add_node(self.app.get_method(cmsix).get_aqname())

        rem_nodes = [ cmsix ]
        done_nodes = []

        while len(rem_nodes) > 0:
            cmsix = rem_nodes.pop()
            done_nodes.append(cmsix)
            methodname = self.app.get_method(cmsix).get_aqname()

            tgts = self._get_rev_method_edges(cmsix)

            for pc in tgts:
                srccmsix = tgts[pc]
                srcname = self.app.get_method(srccmsix).get_aqname()
                dotgraph.add_edge(srcname, methodname)
                if srccmsix not in done_nodes: rem_nodes.append(srccmsix)

        return dotgraph

    def is_callback(self,cmsix):
        self._get_callback_edges()
        return cmsix in self.callbackedges

    def has_target(self,cmsix,pc):
        self._get_edges()
        return (cmsix in self.edges) and (pc in self.edges[cmsix])

    def get_target(self,cmsix,pc):
        self._get_edges()
        if cmsix in self.edges:
            if pc in self.edges[cmsix]:
                return self.edges[cmsix][pc]

    def _get_edges(self):
        if len(self.edges) > 0: return
        for e in self.xnode.find('edges').findall('edge'):
            srccmsix = int(e.get('ix'))
            pc = int(e.get('pc'))
            if not srccmsix in self.edges: self.edges[srccmsix] = {}
            self.edges[srccmsix][pc] = self.cgd.get_target(int(e.get('itgt')))

    def _get_method_edges(self, cmsix):
        edges = {}

        for e in self.xnode.find('edges').findall('edge'):
            if int(e.get('ix')) == cmsix:
                pc = int(e.get('pc'))
                tgt = self.cgd.get_target(int(e.get('itgt')))
                if tgt.is_non_virtual_target() or tgt.is_virtual_target():
                    msix = int(e.get('ms-ix'))
                    if not pc in edges: edges[pc] = {}
                    edges[pc] = (msix, tgt)
        return edges

    def _get_rev_method_edges(self,cmsix):
        edges = {}
        for e in self.xnode.find('edges').findall('edge'):
            msix = int(e.get('ms-ix'))
            tgt = self.cgd.get_target(int(e.get('itgt')))
            for cnix in tgt.cnixs:
                tgtcmsix = self.jd.get_cmsix(cnix, msix)
                if tgtcmsix == cmsix:
                    srcix = int(e.get('ix'))
                    pc = int(e.get('pc'))
                    edges[pc] = srcix
        return edges

    def _getcallbackedges(self):
        if len(self.callbackedges) > 0: return
        for e in self.xnode.find('callback-edges').findall('cb-edge'):
            self.callbackedges.append(int(e.get('ix')))
        

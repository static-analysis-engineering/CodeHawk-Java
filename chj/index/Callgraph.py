# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma and Andrew McGraw
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

from chj.util.DotGraph import DotGraph

import chj.util.fileutil as UF

from typing import Any, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.index.CallgraphDictionary import CallgraphTargetBase
    import xml.etree.ElementTree as ET

class Callgraph():

    def __init__(self, app: "AppAccess", xnode: "ET.Element"):
        self.app = app                   # AppAccess
        self.jd = self.app.jd            # DataDictionary
        self.cgd = self.jd.cgd           # CallgraphDictionary
        self.xnode = xnode
        self.edges: Dict[int, Dict[int, "CallgraphTargetBase"]] = {}             # cms-ix -> pc -> CallgraphTargetBase
        self.callbackedges: List[int] = []     # cms-ix list
        self._get_edges()

    def as_dot(self, cmsix:int) -> Tuple[Dict[str, str], DotGraph]:
        def register_node(dotgraph: DotGraph,
                        cmsix: int, nodes:
                        Dict[str, str]) -> None:
            txt = self.app.get_method(cmsix).get_aqname()
            nodes[txt] = str(cmsix)
            dotgraph.add_node(txt) 

        nodes: Dict[str, str] = {}
        dotgraph = DotGraph("cg_" + str(cmsix))
        register_node(dotgraph, cmsix, nodes)

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
                    if self.jd.is_application_class(cnix):
                        tgtname = self.app.get_method(tgtcmsix).get_aqname()
                        dotgraph.add_edge(methodname, tgtname)
                        register_node(dotgraph, tgtcmsix, nodes)
                        if tgtcmsix not in done_nodes: rem_nodes.append(tgtcmsix)
                    else:
                        if msix in self.jd.mssignatures:
                            tgtname = self.jd.get_cn(cnix).get_name() + '.' + self.jd.mssignatures[msix][0]
                        else:
                            tgtname = self.jd.get_cn(cnix).get_name()
                        dotgraph.add_edge(methodname, tgtname)
        return (nodes, dotgraph)

    def as_rev_dot(self, cmsix: int) -> DotGraph:
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

    def is_callback(self, cmsix: int) -> bool:
        self._getcallbackedges()
        return cmsix in self.callbackedges

    def has_target(self, cmsix: int, pc: int) -> bool:
        self._get_edges()
        return (cmsix in self.edges) and (pc in self.edges[cmsix])

    def get_target(self, cmsix: int, pc: int) -> "CallgraphTargetBase":
        self._get_edges()
        if cmsix in self.edges:
            if pc in self.edges[cmsix]:
                return self.edges[cmsix][pc]
        raise UF.CHJError("Callgraph Target missing from cmsix : " + str(cmsix) + ", pc: " + str(pc))

    def _get_edges(self) -> None:
        errormsg = 'missing from xml for callgraph'

        if len(self.edges) > 0: return
        for e in UF.safe_find(self.xnode, 'edges', 'edges ' + errormsg).findall('edge'):
            srccmsix = UF.safe_get(e, 'ix', 'ix ' + errormsg , int)
            pc = UF.safe_get(e, 'pc', 'pc ' + errormsg , int)
            if not srccmsix in self.edges: self.edges[srccmsix] = {}
            self.edges[srccmsix][pc] = self.cgd.get_target(UF.safe_get(e, 'itgt', 'itgt ' + errormsg, int))

    def _get_method_edges(self, cmsix: int) -> Dict[int, Tuple[int, "CallgraphTargetBase"]]:
        edges: Dict[int, Tuple[int, "CallgraphTargetBase"]] = {}
        errormsg = ' missing from xml for method with cmsix ' + str(cmsix)

        for e in UF.safe_find(self.xnode, 'edges', 'edges ' + errormsg).findall('edge'):
            if UF.safe_get(e, 'ix', 'ix ' + errormsg, int) == cmsix:
                pc = UF.safe_get(e, 'pc', 'pc ' + errormsg, int)
                tgt = self.cgd.get_target(UF.safe_get(e, 'itgt', 'itgt ' + errormsg, int))
                if tgt.is_non_virtual_target() or tgt.is_virtual_target():
                    msix = UF.safe_get(e, 'ms-ix', 'ms-ix ' + errormsg, int)
                    edges[pc] = (msix, tgt)
        return edges

    def _get_rev_method_edges(self, cmsix: int) -> Dict[int, int]:
        errormsg = ' missing from xml for method with cmsix ' + str(cmsix)

        edges = {}
        for e in UF.safe_find(self.xnode, 'edges', 'edges ' + errormsg).findall('edge'):
            msix = UF.safe_get(e, 'ms-ix', 'ms-ix ' + errormsg, int)
            tgt = self.cgd.get_target(UF.safe_get(e, 'itgt', 'itgt ' + errormsg, int))
            for cnix in tgt.cnixs:
                tgtcmsix = self.jd.get_cmsix(cnix, msix)
                if tgtcmsix == cmsix:
                    srcix = UF.safe_get(e, 'ix', 'ix ' + errormsg, int)
                    pc = UF.safe_get(e, 'pc', 'pc ' + errormsg, int)
                    edges[pc] = srcix
        return edges

    def _getcallbackedges(self) -> None:
        if len(self.callbackedges) > 0: return
        for e in UF.safe_find(self.xnode, 'callback-edges', 'callback-edges missing from xml').findall('cb-edge'):
            self.callbackedges.append(UF.safe_get(e, 'ix', 'ix missing callback-edges xml', int))
        

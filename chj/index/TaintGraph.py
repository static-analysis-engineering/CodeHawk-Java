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
import chj.util.dotutil as UD
import chj.util.graphutil as UG

import chj.index.Taint as T

from typing import cast, Dict, List, Optional, Set, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    import xml.etree.ElementTree as ET

class TaintGraph():

    def __init__(self,
            app: "AppAccess",
            appname: str,
            taintsourceid: str,
            loops: bool=False,
            sink: Optional[str]=None) -> None:
        self.app = app                   # AppAccess
        self.jd = self.app.jd            # DataDictionary
        self.loops = loops
        self.sink = sink

        self.xnodes: "ET.Element"
        self.xedges: "ET.Element"

        self.pathnodes: List[int] = []
        self.nodes: List[int] = []
        self.edges: List[Tuple[int, int]] = []

        self._build_graph(appname, taintsourceid)

    def _get_edges(self, appname: str, taintsourceid: str) -> None:
        try:
            (path,_) = UF.get_engagement_app_jars(appname)
            UF.check_analysisdir(path)
            xtrail = UF.get_data_taint_trail_xnode(path,int(taintsourceid))
        except UF.CHJError as e:
            print(str(e.wrap()))
            return

        self.xnodes = UF.safe_find(xtrail, 'node-dictionary', 'node-dictionary missing from xml')
        self.xedges = UF.safe_find(xtrail, 'edges' , 'edges missing from xml')

        self.nodes = [ UF.safe_get(n, 'ix', 'ix missing from xml', int) for n in self.xnodes.findall('tn') ]

    def _get_root_node(self, nodes: List[int], enode: "ET.Element") -> int:
        tgts = []
        for en in enode.findall('edge'):
            tgts.append(UF.safe_get(en, 'src', 'src missing from xml for taintgraph', int))
        for n in nodes:
            if not n in tgts:
                return n
        raise UF.CHJError("Root missing from TaintGraph")

    def _build_graph(self, appname: str, taintsourceid: str) -> None:
        if self.jd.ttd is None:
            raise UF.CHJError("Taint analysis results not found! Please create them first")

        self._get_edges(appname, taintsourceid)

        pathnodes: Set[int] = set([])

        if (not self.sink is None) or self.loops:
            sinkids = []

            if not self.sink is None:
                for n in self.nodes:
                    cms = self.jd.ttd.get_taint_node_type(n)
                    if self.sink in str(cms):
                        sinkids.append(n)
                if len(sinkids) == 0:
                    return

            if self.loops:
                for n in self.nodes:
                    cms = self.jd.ttd.get_taint_node_type(n)
                    if cms.is_var() and str(cast(T.VariableTaintNode, cms).get_variable()) == 'lc':
                        sinkids.append(n)

            edge_adjacencylists: Dict[int, List[int]] = {}
            for m in self.xedges.findall('edge'):
                src = UF.safe_get(m, 'src', 'src missing from xml', int)
                tgts = [ int(x) for x in UF.safe_get(m, 'tgts', 'tgts missing from xml', str).split(',') ]
                for t in tgts:
                    edge_adjacencylists.setdefault(t,[])
                    edge_adjacencylists[t].append(src)

            srcid = self._get_root_node(self.nodes, self.xedges)

            srcname = str(self.jd.ttd.get_taint_node_type(srcid))
            for sinkid in sinkids:
                sinkname = str(self.jd.ttd.get_taint_node_type(sinkid))

            for sinkid in sinkids:
                if sinkid in pathnodes: continue
                g = UG.DirectedGraph(self.nodes,edge_adjacencylists)
                g.find_paths(srcid,sinkid)
                for p in g.paths:
                    pathnodes = pathnodes.union(p)

        # if no restrictions include all nodes
        if len(pathnodes) == 0:
            pathnodes = set(self.nodes)

        edges = []
        for j in self.xedges.findall('edge'):
            src = UF.safe_get(j, 'src', 'src missing from xml', int)
            if src in self.nodes:
                tgts = [ int(x) for x in UF.safe_get(j, 'tgts', 'tgts missing from xml', str).split(',') ]
                for tgt in tgts:
                    if tgt in self.nodes:
                        edges.append((src,tgt))

        self.pathnodes = list(pathnodes)
        self.edges = edges
        return

    def as_dot(self, taintsourceid: str) -> DotGraph:
        if self.app.jd.ttd is None:
            raise UF.CHJError("Taint analysis results not found! Please create them first")

        graphname = 'trail_' + str(taintsourceid)
        dotgraph = DotGraph(graphname)
        for n in self.nodes:
            if not n in self.pathnodes: continue
            color = None
            cms = self.app.jd.ttd.get_taint_node_type(n)
            shaded = cms.is_call()
            cmslabel = cms.dotlabel()
            if cms.is_var():
                cms = cast(T.VariableTaintNode, cms)
                if str(cms.get_variable()) == 'lc':
                    color = 'red'
                if str(cms.get_variable()) == 'return':
                    color = 'green'
            elif cms.is_conditional():
                color = 'yellow'
            dotgraph.add_node(str(n),str(cmslabel),shaded=shaded,fillcolor=color)
        for (src,tgt) in self.edges:
            if src in self.pathnodes and tgt in self.pathnodes:
                dotgraph.add_edge(str(tgt),str(src))
        return dotgraph 

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

import chj.util.fileutil as UF
import chj.util.dotutil as UD
import chj.util.graphutil as UG

class TaintGraph():

    def __init__(self,app,appname,taintsourceid,loops=False,sink=None):
        self.app = app                   # AppAccess
        self.jd = self.app.jd            # DataDictionary
        self.loops = loops
        self.sink = sink

        self.xnodes = None
        self.xedges = None

        self.pathnodes = []
        self.nodes = []
        self.edges = []

        self._build_graph(appname, taintsourceid)

    def _get_edges(self, appname, taintsourceid):
        try:
            (path,_) = UF.get_engagement_app_jars(appname)
            UF.check_analysisdir(path)
            xtrail = UF.get_data_taint_trail_xnode(path,int(taintsourceid))
        except UF.CHJError as e:
            print(str(e.wrap()))
            return

        self.xnodes = xtrail.find('node-dictionary')
        self.xedges = xtrail.find('edges')

        self.nodes = [ int(n.get('ix')) for n in self.xnodes.findall('tn') ]

    def _get_root_node(self,nodes,enode):
        tgts = []
        for n in enode.findall('edge'):
            tgts.append(int(n.get('src')))
        for n in nodes:
            if not n in tgts:
                return n

    def _build_graph(self, appname, taintsourceid):
        self._get_edges(appname, taintsourceid)

        pathnodes = set([])

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
                    if cms.is_var() and str(cms.get_variable()) == 'lc':
                        sinkids.append(n)

            edge_adjacencylists = {}
            for n in self.xedges.findall('edge'):
                src = int(n.get('src'))
                tgts = [ int(x) for x in n.get('tgts').split(',') ]
                for t in tgts:
                    edge_adjacencylists.setdefault(t,[])
                    edge_adjacencylists[t].append(src)

            srcid = self._get_root_node(self.nodes,self.xedges)

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
            pathnodes = self.nodes

        edges = []
        for n in self.xedges.findall('edge'):
            src = int(n.get('src'))
            if src in self.nodes:
                tgts = [ int(x) for x in n.get('tgts').split(',') ]
                for tgt in tgts:
                    if tgt in self.nodes:
                        edges.append((src,tgt))

        self.pathnodes = pathnodes
        self.edges = edges
        return

    def as_dot(self, taintsourceid):
        graphname = 'trail_' + str(taintsourceid)
        dotgraph = DotGraph(graphname)
        for n in self.nodes:
            if not n in self.pathnodes: continue
            color = None
            cms = self.app.jd.ttd.get_taint_node_type(n)
            shaded = cms.is_call()
            cmslabel = cms.dotlabel()
            if cms.is_var():
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

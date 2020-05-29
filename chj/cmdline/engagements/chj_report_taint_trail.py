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
"""Creates a graphical representation of a taint trail."""

import argparse
import time

from contextlib import contextmanager

import chj.util.fileutil as UF
import chj.util.dotutil as UD
import chj.util.graphutil as UG

from chj.index.AppAccess import AppAccess
from chj.util.DotGraph import DotGraph

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('taintsourceid',type=int,
                            help='id of the taint source (get from chj_report_taint_origins)')
    parser.add_argument('--sink',help='(partial) name of a node to restrict paths to as a destination')
    parser.add_argument('--loops',help='restrict paths to destinations that represent loop counters',
                            action='store_true')
    args = parser.parse_args()
    return args

@contextmanager
def timing(activity):
    t0 = time.time()
    yield
    print('\n' + ('=' * 80) + 
          '\nCompleted ' + activity + ' in ' + str(time.time() - t0) + ' secs' +
          '\n' + ('=' * 80))

# return the root of the taint graph
def get_root_node(nodes,enode):
    tgts = []
    for n in enode.findall('edge'):
        tgts.append(int(n.get('src')))
    for n in nodes:
        if not n in tgts:
            return n

if __name__ == '__main__':

    args = parse()
    try:
        (path,_) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
        xtrail = UF.get_data_taint_trail_xnode(path,int(args.taintsourceid))        
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    app = AppAccess(path)

    xnodes = xtrail.find('node-dictionary')
    xedges = xtrail.find('edges')

    nodes = [ int(n.get('ix')) for n in xnodes.findall('tn') ]
    pathnodes = set([])

    if (not args.sink is None) or args.loops:
        with timing('find paths'):
            sinkids = []

            if not args.sink is None:
                for n in nodes:
                    cms = app.jd.ttd.get_taint_node_type(n)
                    if args.sink in str(cms):
                        sinkids.append(n)
                if len(sinkids) == 0:
                    print('*' * 80)
                    print('No node found that contains ' + args.sink)
                    print('*' * 80)
                    exit(1)

            if args.loops:
                for n in nodes:
                    cms = app.jd.ttd.get_taint_node_type(n)
                    if cms.is_var() and str(cms.get_variable()) == 'lc':
                        sinkids.append(n)

            edge_adjacencylists = {}
            for n in xedges.findall('edge'):
                src = int(n.get('src'))
                tgts = [ int(x) for x in n.get('tgts').split(',') ]
                for t in tgts:
                    edge_adjacencylists.setdefault(t,[])
                    edge_adjacencylists[t].append(src)

            srcid = get_root_node(nodes,xedges)

            srcname = str(app.jd.ttd.get_taint_node_type(srcid))
            print('Generating paths from ' + srcname + ' to ')
            for sinkid in sinkids:
                sinkname = str(app.jd.ttd.get_taint_node_type(sinkid))
                print(' - ' + sinkname)


            for sinkid in sinkids:
                if sinkid in pathnodes: continue   
                g = UG.DirectedGraph(nodes,edge_adjacencylists)
                print('Find path to ' + str(app.jd.ttd.get_taint_node_type(sinkid)))
                g.find_paths(srcid,sinkid)
                for p in g.paths:
                    pathnodes = pathnodes.union(p)

    # if no restrictions include all nodes
    if len(pathnodes) == 0:
        pathnodes = nodes

    edges = []
    for n in xedges.findall('edge'):
        src = int(n.get('src'))
        if src in pathnodes:
            tgts = [ int(x) for x in n.get('tgts').split(',') ]
            for tgt in tgts:
                if tgt in pathnodes:
                    edges.append((src,tgt))

    with timing('creating graph (' + str(len(pathnodes)) + ' nodes; '
                                             + str(len(edges))  + ' edges)'):
        graphname = 'trail_' + str(args.taintsourceid)
        dotgraph = DotGraph(graphname)
        for n in nodes:
            if not n in pathnodes: continue
            color = None
            cms = app.jd.ttd.get_taint_node_type(n)
            shaded = cms.is_call()
            cmslabel = cms.dotlabel()
            if cms.is_var():
                if str(cms.get_variable()) == 'lc':
                    color = 'red'
                if str(cms.get_variable()) == 'return':
                    color = 'green'
            elif cms.is_conditional():
                color = 'yellow'
            dotgraph.add_node(str(n),str(cmslabel),shaded=shaded,color=color)
        for (src,tgt) in edges:
            if src in pathnodes and tgt in pathnodes:
                dotgraph.add_edge(str(tgt),str(src))
        UD.print_dot(app.path,dotgraph)

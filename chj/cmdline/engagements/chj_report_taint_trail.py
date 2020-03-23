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

import chj.util.fileutil as UF
import chj.util.dotutil as UD

from chj.index.AppAccess import AppAccess
from chj.reporting.LoopSummary import LoopSummary
from chj.util.DotGraph import DotGraph

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('taintsourceid',type=int,
                            help='id of the taint source (get from chj_report_taint_origins)')
    args = parser.parse_args()
    return args

def node_tostring(app,index):
    ttd = app.jd.ttd
    return str(ttd.get_taint_node_type(index))
    

if __name__ == '__main__':

    args = parse()
    try:
        (path,_) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    app = AppAccess(path)

    try:
        xnode = UF.get_data_taint_trail_xnode(path,int(args.taintsourceid))
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    dnode = xnode.find('node-dictionary')
    enode = xnode.find('edges')

    nodes = {}
    for n in dnode.findall('tn'):
        nodes[int(n.get('ix'))] = int(n.get('ut'))

    edges = []
    for n in enode.findall('edge'):
        src = int(n.get('src'))
        tgts = [ int(x) for x in n.get('tgts').split(',') ]
        for tgt in tgts:
            edges.append((src,tgt))

    graphname = 'trail_' + str(args.taintsourceid)
    dotgraph = DotGraph(graphname)
    for n in nodes:
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
    for (src,tgt) in edges: dotgraph.add_edge(str(tgt),str(src))
    UD.print_dot(app.path,dotgraph)

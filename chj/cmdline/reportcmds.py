# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Andrew McGraw
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2021 Andrew McGraw
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

import argparse, sys

import chj.cmdline.AnalysisManager as AM
import chj.cmdline.commandutils as UCC

import chj.util.fileutil as UF
import chj.util.dotutil as UD
import chj.util.printutil as UP
import chj.util.graphutil as UG

import chj.reporting.ObjectFields as RPO
import chj.reporting.ObjectsCreated as RPC
import chj.reporting.StaticFields as RPS

from chj.index.AppAccess import AppAccess
from chj.index.Taint import VariableTaintNode
from chj.reporting.BranchConditions import BranchConditions
from chj.reporting.CostSummary import CostSummary
from chj.reporting.ExceptionHandlers import ExceptionHandlers
from chj.reporting.LoopSummary import LoopSummary
from chj.reporting.ObjectSizes import ObjectSizes
from chj.reporting.Recursion import Recursion
from chj.reporting.TaintOrigins import TaintOrigins

from chj.util.DotGraph import DotGraph

from contextlib import contextmanager

from typing import cast, Dict, List, Optional, NoReturn, Set, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    import chj.index.CallgraphDictionary as CGD
    import xml.etree.ElementTree as ET

    VIRTUAL_TARGET = Union[CGD.VirtualTargets, CGD.ConstrainedVirtualTargets]

def branches(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    includes: Optional[str] = args.includes
    save: bool = args.save

    path = UCC.check_app_analysisdir(appname)

    app = AppAccess(path)

    lines = []

    headername = appname
    lines.append(UP.reportheader('Branch Conditions', headername))
    if includes:
        lines.append(BranchConditions(app).toincludestring(includes))
    else:
        lines.append(BranchConditions(app).tostring())

    if save:
        UCC.save(path, 'branch_conditions_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def callgraph(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    multiple: bool = args.multiple

    path = UCC.check_app_analysisdir(appname)

    app = AppAccess(path)
    callgraph = app.get_callgraph()

    def is_multiple(cmsedges: Dict[int, "CGD.CallgraphTargetBase"]) -> bool:
        for pc in cmsedges:
            tgt = cmsedges[pc]
            if tgt.is_virtual_target():
                if cast("VIRTUAL_TARGET", tgt).get_length() > 1:
                    return True
        else:
            return False

    for cmsix in callgraph.edges:
        cmsedges = callgraph.edges[cmsix]
        cms = app.jd.get_cms(cmsix)
        if is_multiple(cmsedges) or (not multiple):
            print('\n' + str(cms) + ' (' + str(cmsix) + ')')
            for pc in sorted(cmsedges):
                tgt = cmsedges[pc]
                if (not multiple) or (tgt.is_virtual_target() and cast("VIRTUAL_TARGET", tgt).get_length() > 1):
                    print('  ' + str(pc).rjust(4) + ': ' + str(cmsedges[pc]))
    exit(0)

def class_methodcalls(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    classname: str = args.classname
    save: bool = args.save

    path = UCC.check_app_analysisdir(appname)

    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Named method calls to ' + classname, headername))

    results = []
    def f(cmsix: int, m: "JavaMethod") -> None:
        results.append((cmsix,m.get_class_method_calls(classname)))
    app.iter_methods(f)

    for (cmsix,mmethodcalls) in results:
        if len(mmethodcalls) > 0:
            lines.append('\n'+ app.jd.get_cms(cmsix).get_aqname())
            for (pc,i) in mmethodcalls:
                loopdepth = i.get_loop_depth()
                loopdepth_str = 'L' + str(loopdepth) if loopdepth > 0 else '  '
                lines.append(str(pc).rjust(6) + '  ' + loopdepth_str + '  ' + str(i))

    if save:
        UCC.save(path, 'method_calls_to_' + classname + '.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def costmodel(args: argparse.Namespace) -> NoReturn:
    #arguments

    appname: str = args.appname
    verbose: bool = args.verbose
    loops: bool = args.loops
    save: bool = args.save
    namerestriction: List[str] = args.namerestriction

    path = UCC.check_app_analysisdir(appname)

    app = AppAccess(path)
    costreport = CostSummary(app)

    if not namerestriction is None:
        def namefilter(name: str) -> bool:
            for n in namerestriction:
                if not n in name:
                    return False
            return True
    else:
        namefilter = lambda name:True

    lines = []
    headername = appname
    lines.append(UP.reportheader('Cost Model Summary',headername))

    with UCC.timing('Print cost report'):
        lines.append(costreport.to_string(namefilter=namefilter))
        lines.append(costreport.to_side_channels_string())
        if verbose: lines.append(costreport.to_verbose_string(namefilter=namefilter))
        if loops: lines.append(costreport.to_loop_bounds_string())

    if save:
        UCC.save(path, 'cost_model_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def exception_handlers(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    save: str = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)
    
    lines = []
    headername = appname
    lines.append(UP.reportheader('Exception Handlers', headername))
    lines.append(ExceptionHandlers(app).tostring())

    if save:
        UCC.save(path, 'exception_handlers_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def loaded_strings(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    substring: Optional[str] = args.substring
    save: bool = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)
    results = app.get_loaded_strings(substring=substring)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Loaded strings', headername))
    print('-' * 80)
    for (cmsix,methodresults) in sorted(results):
        if len(methodresults) == 0: continue
        lines.append('\n' + str(app.jd.get_cms(cmsix).get_aqname()))
        for (pc, instr) in sorted(methodresults):
            lines.append((str(pc).rjust(4) + '  ' + str(instr)))

    if save:
        UCC.save(path, 'loaded_strings_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def loops(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    taintorigins: Optional[List[int]] = args.taintorigins
    save: bool = args.save

    path = UCC.check_app_analysisdir(appname)

    taintlist = []
    if not taintorigins is None: taintlist = taintorigins
    taintnodes = []

    app = AppAccess(path)

    for t in taintlist:
        xnode = UF.get_data_taint_trail_xnode(path,int(t))
        if xnode is None:
            print('No taint trail found for id ' + str(t))
            exit(1)
        dnode = UF.safe_find(xnode, 'node-dictionary', 'node-dictionary missing from xml')
        for n in dnode.findall('tn'):
            taintnodes.append(UF.safe_get(n, 'ix', 'ix missing from xml', int))

    lines = []
    headername = appname
    lines.append(UP.reportheader('Loop Summary', headername))
    loopsummary = LoopSummary(app,sources=list(taintnodes))
    if len(taintlist) > 0:
        if app.jd.ttd is not None:
            for tn in taintlist:
                lines.append(str(tn).rjust(4) + '  '
                                 + str(app.jd.ttd.get_taint_origin(tn)))
            lines.append('-' * 80)
    lines.append(loopsummary.to_string())
    lines.append('\n\n')
    lines.append(loopsummary.list_to_string())

    if save:
        UCC.save(path, 'taint_origins_reports.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def named_methodcalls(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    name: str = args.name
    save: Optional[str] = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Named method calls to ' + name,headername))

    results = []
    def f(cmsix: int, m: "JavaMethod") -> None:
        results.append((cmsix, m.get_named_method_calls(name)))
    app.iter_methods(f)

    for (cmsix,mmethodcalls) in results:
        if len(mmethodcalls) > 0:
            lines.append('\n'+ app.jd.get_cms(cmsix).get_aqname())
            for (pc,i) in mmethodcalls:
                loopdepth = i.get_loop_depth()
                loopdepth_str = 'L' + str(loopdepth) if loopdepth > 0 else '  '
                lines.append(str(pc).rjust(6) + '  ' + loopdepth_str + '  ' + str(i))

    if save:
        UCC.save(path, 'method_calls_to_' + name + '.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def object_field_writes(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    save: Optional[str] = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Object Field Accesses', headername))
    lines.append(RPO.ObjectFields(app).to_string())

    if save:
        UCC.save(path, 'object_field_access_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def objects_created(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    save: Optional[str] = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Objects Created', headername))
    lines.append(RPC.ObjectsCreated(app).to_string())

    if save:
        UCC.save(path, 'objects_created_reports.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def object_sizes(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    save: Optional[str] = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Object Sizes', headername))
    lines.append(ObjectSizes(app).to_string())

    if save:
        UCC.save(path, 'objectsizes_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def recursive_functions(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    save: Optional[str] = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    recursionreport = Recursion(app)
    recursionstring = recursionreport.to_string()

    if save:
        UCC.save(path, 'recursive_functions_report.txt', [recursionstring])
    else:
        print(recursionstring)
    exit(0)

def reflective_calls(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    save: Optional[str] = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Reflective method calls', headername))

    reflective_names = [ 
        "forName",
        "getDeclaredClassed",
        "getDeclaredConstructors",
        "getDeclaredField",
        "getDeclaredFields",
        "getDeclaredMethod",
        "getDeclaredMethods",
        "getField",
        "getFields",
        "getMethod",
        "getMethods"]

    results = []
    def f(cmsix: int, m: "JavaMethod") -> None:
        for n in reflective_names:
            results.append((cmsix, m.get_named_method_calls(n)))
    app.iter_methods(f)

    for (cmsix,mmethodcalls) in results:
        if len(mmethodcalls) > 0:
            lines.append('\n'+ app.jd.get_cms(cmsix).get_aqname())
            for (pc,i) in mmethodcalls:
                lines.append(str(pc).rjust(6) + '  ' + str(i))

    if save:
        UCC.save(path, 'reflective_calls.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def static_field_inits(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    save: Optional[str] = args.save

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Static Field Accesses', headername))
    lines.append(RPS.StaticFields(app).to_string())

    if save:
        UCC.save(path, 'static_fields_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def taint_origins(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    source: Optional[str] = args.source
    save: Optional[str] = args.source

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    headername = appname
    lines.append(UP.reportheader('Taint Origins', headername))
    lines.append(TaintOrigins(app).tostring(source))

    if save:
        UCC.save(path, 'taint_origins_report.txt', lines)
    else:
        print('\n'.join(lines))
    exit(0)

def taint_trail(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    taintsourceid: int = args.taintsourceid
    sink: Optional[str] = args.sink
    loops: bool = args.loops

    try:
        (path,_) = UF.get_engagement_app_jars(appname)
        UF.check_analysisdir(path)
        xtrail = UF.get_data_taint_trail_xnode(path,int(taintsourceid))
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    app = AppAccess(path)
    if app.jd.ttd is None:
        raise UF.CHJError('Taint analysis results missing from xml! Please create them first')

    xnodes = UF.safe_find(xtrail, 'node-dictionary', 'node-dictionary missing from xml')
    xedges = UF.safe_find(xtrail, 'edges', 'edges missing from xml')

    nodes = [ UF.safe_get(n, 'ix', 'ix missing from xml', int) for n in xnodes.findall('tn') ]
    pathnodes: Set[int] = set([])

    # return the root of the taint graph
    def get_root_node(nodes: List[int], enode: "ET.Element") -> int:
        tgts = []
        for n in enode.findall('edge'):
            tgts.append(UF.safe_get(n, 'src', 'src missing from xml', int))
        for j in nodes:
            if not j in tgts:
                return j
        raise UF.CHJError('Root node missing from taint graph!')

    if (not sink is None) or loops:
        with UCC.timing('find paths'):
            sinkids = []

            if not sink is None:
                for n in nodes:
                    cms = app.jd.ttd.get_taint_node_type(n)
                    if sink in str(cms):
                        sinkids.append(n)
                if len(sinkids) == 0:
                    print('*' * 80)
                    print('No node found that contains ' + sink)
                    print('*' * 80)
                    exit(1)

            if loops:
                for n in nodes:
                    cms = app.jd.ttd.get_taint_node_type(n)
                    if cms.is_var():
                        cms = cast(VariableTaintNode,  cms)
                        if str(cms.get_variable()) == 'lc':
                            sinkids.append(n)

            edge_adjacencylists: Dict[int, List[int]] = {}
            for m in xedges.findall('edge'):
                src = UF.safe_get(m, 'src', 'src missing from xml', int)
                tgts = [ int(x) for x in UF.safe_get(m, 'tgts', 'tgts missing from xml', str).split(',') ]
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
        pathnodes = set(nodes)

    edges = []
    for m in xedges.findall('edge'):
        src = UF.safe_get(m, 'src', 'src missing from xml', int)
        if src in pathnodes:
            tgts = [ int(x) for x in UF.safe_get(m, 'tgts', 'tgts missing from xml', str).split(',') ]
            for tgt in tgts:
                if tgt in pathnodes:
                    edges.append((src,tgt))

    with UCC.timing('creating graph (' + str(len(pathnodes)) + ' nodes; '
                                             + str(len(edges))  + ' edges)'):
        graphname = 'trail_' + str(taintsourceid)
        dotgraph = DotGraph(graphname)
        for n in nodes:
            if not n in pathnodes: continue
            color = None
            cms = app.jd.ttd.get_taint_node_type(n)
            shaded = cms.is_call()
            cmslabel = cms.dotlabel()
            if cms.is_var():
                cms = cast(VariableTaintNode, cms)
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
    exit(0)

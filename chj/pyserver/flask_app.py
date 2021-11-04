# ------------------------------------------------------------------------------
# CodeHawk Binary Analyzer
# Author: Andrew McGraw
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

import json
import os
import traceback

import xml.etree.ElementTree as ET

from flask import Flask, render_template, render_template_string, jsonify, request, Response, Markup

import chj.util.fileutil as UF
import chj.util.xmlutil as UX
import chj.index.AppAccess as AP
import chj.util.dotutil as UD
import chj.util.svgutil as UG
import chj.util.analysisutil as UA

from chj.index.TaintGraph import TaintGraph

from chj.reporting.BytecodeReport import BytecodeReport
from chj.reporting.BranchConditions import BranchConditions
from chj.reporting.CostSummary import CostSummary
from chj.reporting.ExceptionHandlers import ExceptionHandlers
from chj.reporting.LoopSummary import LoopSummary
from chj.reporting.Recursion import Recursion
from chj.reporting.StaticFields import StaticFields
from chj.reporting.TaintOrigins import TaintOrigins

from typing import Any, Dict, List, Tuple, Union, TYPE_CHECKING

# ======================================================================
# Rest API
# ======================================================================

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loadprojects')
def loadprojects() -> Response:
    result: Dict[str, Dict[str, Any]] = {}
    result['meta'] = {}
    try:
        projects: Dict[str, List[str]] = {}
        appfile = UF.get_engagements_data_file()
        if not appfile is None:
            for e in sorted(appfile):
                if not e in projects: projects[e] = []
                for app in sorted(appfile[e]['apps']):
                    projects[e].append(app)
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = projects
    return jsonify(result)

@app.route('/branches/<engagement>/<project>')
def loadbranches(engagement: str, project: str) -> Response:
    result: Dict[str, Dict[str, Any]] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        branchsummary = BranchConditions(app).as_dictionary()
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = branchsummary
    return jsonify(result)

@app.route('/costs/<engagement>/<project>')
def loadcosts(engagement: str, project: str) -> Response:
    result: Dict[str, Dict[str, Any]] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        costreport = CostSummary(app)
        costsummary = costreport.as_dictionary()
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok' 
        result['content'] = costsummary
    return jsonify(result)

@app.route('/exceptions/<engagement>/<project>')
def loadexceptions(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        exceptionreport = ExceptionHandlers(app)
        exceptionsummary = exceptionreport.as_dictionary()
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'       
        result['content'] = exceptionsummary
    return jsonify(result)

@app.route('/loops/<engagement>/<project>')
def loadloops(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        loopsummary = LoopSummary(app).as_dictionary()
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'       
        result['content'] = loopsummary
    return jsonify(result)

@app.route('/project/<engagement>/<project>')
def loadproject(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        classes = {}
        def f(myclass):
            classes[myclass.get_name()] = str(myclass.cnix)
        app.iter_classes(f)
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = classes
    return jsonify(result)

@app.route('/strings/<engagement>/<project>')
def loadstrings(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        strings = app.get_loaded_strings()
        stringsummary = {}
        for (cmsix, methodresults) in sorted(strings):
            if len(methodresults) == 0: continue
            methodname = str(app.jd.get_cms(cmsix).get_aqname())
            methodstrings: Dict[str, Any] = {}

            methodstrings['name'] = methodname
            methodstrings['pcs'] = {}
            for (pc, instr) in sorted(methodresults):
                methodstrings['pcs'][pc] = instr
            stringsummary[cmsix] = methodstrings
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'       
        result['content'] = stringsummary
    return jsonify(result)
    
@app.route('/recursive/<engagement>/<project>')
def loadrecursive(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        recursionsummary = Recursion(app).as_dictionary()
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'       
        result['content'] = recursionsummary
    return jsonify(result)
    
@app.route('/reflective/<engagement>/<project>')
def loadreflective(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)

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
        "getMethods"
        ] 

        methods = []
        def f(cmsix,m):
            for n in reflective_names:
                methods.append((cmsix,m.get_named_method_calls(n)))
        app.iter_methods(f)


        reflectionsummary: Dict[int, Any] = {}
        for (cmsix,mmethodcalls) in methods:
            if len(mmethodcalls) > 0:
                name = app.jd.get_cms(cmsix).get_aqname()

                pcs = {}
                for (pc,i) in mmethodcalls:
                    pcs[pc] = str(i)

                if not cmsix in reflectionsummary:
                    reflectionsummary[cmsix] = {}
                    reflectionsummary[cmsix]['name'] = name
                    reflectionsummary[cmsix]['pcs'] = pcs
                else:
                    reflectionsummary[cmsix]['pcs'].update(pcs)
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'       
        result['content'] = reflectionsummary
    return jsonify(result)

@app.route('/staticfieldinits/<engagement>/<project>')
def loadstaticfieldinits(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        sfsummary = StaticFields(app).as_dictionary()
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'       
        result['content'] = sfsummary
    return jsonify(result)

@app.route('/taintorigins/<engagement>/<project>')
def loadtaintorigins(engagement: str, project: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        taintsummary = TaintOrigins(app).as_dictionary() 
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'       
        result['content'] = taintsummary
    return jsonify(result)

@app.route('/taint/<engagement>/<project>/<index>', methods=['GET', 'POST'])
def loadtaintgraph(engagement: str, project: str, index: str) -> Union[str, Dict[str, Any]]:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    loops = False
    sink = None
    try:
        title = engagement + ":" + project + ":" + index
        app = load_engagement_app(engagement, project)
    
        if app.jd.ttd is None:
            raise UF.CHJError('Taint analysis results do not exist! Please create them first')

        name = str(app.jd.ttd.get_taint_origin(int(index)))

        new_app = UA.analyze_taint_propagation(project, int(index))
        if new_app is not None:
            app = new_app

        if request.method == 'POST':
            req = request.form
            loops = True if 'loops' in req else False
            sink = req['sinkid'] if 'sinkid' in req else None

        taintgraph = TaintGraph(app, project, index, loops=loops, sink=sink)
        dotgraph = taintgraph.as_dot(index)
        svggraph = UG.get_svg(app.path, dotgraph)
        svg = ET.tostring(svggraph.getroot(), encoding='unicode', method='html')

        if request.method == 'GET':
            template = render_template('taint.html', title=title, body=Markup(svg), name=name,
                                        eng=engagement, proj=project, index=index)
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
        return result
    else:
        if request.method == 'GET':
            return template
        elif request.method == 'POST':
            result['meta']['status'] = 'ok'
            result['content'] = {}
            result['content']['svg'] = Markup(svg)
            return result
        else:
            raise UF.CHJError("Unknown Methods Parameter. Options are \"Get\" and \"Post\"")

def load_engagement_app(engagement: str, project: str) -> AP.AppAccess:
    (path, jars) = UF.get_engagement_app_data(project)
    UF.check_analysisdir(path)
    app = AP.AppAccess(path)
    return app

def get_method_body(engagement: str, project: str, cmsix: int) -> Tuple[str, str]:
    app = load_engagement_app(engagement, project)
    mname = app.get_method(int(cmsix)).get_qname()
    bytecodereport = BytecodeReport(app, int(cmsix)).as_list()
    body = ET.tostring(mk_method_code_table(bytecodereport),
                                        encoding='unicode', method='html')
    return (mname, body)

@app.route('/method/<engagement>/<project>/<cmsix>')
def load_method(engagement: str, project: str, cmsix: str) -> Union[str, Response]:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        (mname, body) = get_method_body(engagement, project, int(cmsix))
        title = engagement + ":" + project + ":" + cmsix
        template = render_template('method.html', title=title, body=Markup(body), name=mname,
                                        eng=engagement, proj=project, index=cmsix)
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
        return jsonify(result)
    else:
        return template

@app.route('/class/<engagement>/<project>/<cnix>')
def load_bytecode(engagement: str, project: str, cnix: str) -> Union[str, Response]:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        cname = app.get_class(int(cnix)).get_qname()
        bytecode = app.get_class(int(cnix)).as_dictionary()
        body = Markup(ET.tostring(mk_class_code_table(bytecode, engagement, project), 
                                        encoding='unicode', method='html')) 
        title = engagement + ":" + project + ":" + cnix
        template = render_template('class.html', title=title, body=body, name=cname, 
                                        eng=engagement, proj=project, index=cnix)
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
        return jsonify(result)
    else:
        return template

@app.route('/methodcg/<engagement>/<project>/<cmsix>')
def load_method_cg(engagement: str, project: str, cmsix: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        cg = app.get_callgraph()

        (nodes, dotgraph) = cg.as_dot(int(cmsix))
        svggraph = UG.get_svg(app.path, dotgraph)
        UG.append_cmsixs(svggraph, nodes)

        svg = ET.tostring(svggraph.getroot(), encoding='unicode', method='html')
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = {}
        result['content']['svg'] = svg
    return jsonify(result)

@app.route('/methodrevcg/<engagement>/<project>/<cmsix>')
def load_method_rev_cg(engagement: str, project: str, cmsix: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        revcg = app.get_callgraph()

        dotgraph = revcg.as_rev_dot(int(cmsix))
        svggraph = UG.get_svg(app.path, dotgraph)

        svg = ET.tostring(svggraph.getroot(), encoding='unicode', method='html')
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = {}
        result['content']['svg'] = svg
    return jsonify(result)

@app.route('/methodcfg/<engagement>/<project>/<cmsix>')
def load_method_cfg(engagement: str, project: str, cmsix: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        cfg = app.get_method(int(cmsix)).get_cfg()

        (nodes, dotgraph) = cfg.as_dot()
        svggraph = UG.get_svg(app.path, dotgraph)

        loop_levels = cfg.get_loop_level_counts()
        UG.append_pcs(svggraph, nodes)
        UG.append_loop_levels(svggraph, loop_levels)
        svg = ET.tostring(svggraph.getroot(), encoding='unicode', method='html') 
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = {}
        result['content']['svg'] = svg
    return jsonify(result) 

@app.route('/methodcfgcost/<engagement>/<project>/<cmsix>')
def load_method_cfg_cost(engagement: str, project: str, cmsix: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        cfg = app.get_method(int(cmsix)).get_cfg()
        methodcost = app.get_costmodel().get_method_cost(int(cmsix))

        (nodes, dotgraph) = cfg.as_dot(methodcost=methodcost)
        svggraph = UG.get_svg(app.path, dotgraph)

        loop_levels = cfg.get_loop_level_counts()
        UG.append_pcs(svggraph, nodes)
        UG.append_loop_levels(svggraph, loop_levels)
        svg = ET.tostring(svggraph.getroot(), encoding='unicode', method='html')
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = {}
        result['content']['svg'] = svg
    return jsonify(result)

@app.route('/methodsimplecfgcost/<engagement>/<project>/<cmsix>')
def load_method_simple_cfg_cost(engagement: str, project: str, cmsix: str) -> Response:
    result: Dict[str, Any] = {}
    result['meta'] = {}
    try:
        app = load_engagement_app(engagement, project)
        cfg = app.get_method(int(cmsix)).get_cfg()
        methodcost = app.get_costmodel().get_method_cost(int(cmsix))

        (nodes, dotgraph) = cfg.as_dot(methodcost=methodcost,simplecost=True)
        svggraph = UG.get_svg(app.path, dotgraph)

        loop_levels = cfg.get_loop_level_counts()
        UG.append_pcs(svggraph, nodes)
        UG.append_loop_levels(svggraph, loop_levels)
        svg = ET.tostring(svggraph.getroot(), encoding='unicode', method='html')
    except Exception as e:
        result['meta']['status'] = 'fail'
        result['meta']['reason'] = str(e)
        traceback.print_exc()
    else:
        result['meta']['status'] = 'ok'
        result['content'] = {}
        result['content']['svg'] = svg
    return jsonify(result)

#@app.route('/', defaults={'path': ''})
#@app.route('/<path:path>')
#def catch_all(path):
#    result = {}
#    result['meta'] = {}
#    result['meta']['status'] = 'fail'
#    result['meta']

def mk_class_code_table(f: Dict[str, Dict[str, Any]],
                        engagement: str,
                        project: str) -> ET.Element:
    table = ET.Element('div')
    table.set('id','codetable')

    mt = ET.Element('table')
    mt.set('class', 'methodtable balanced')

    headerrow = mk_header(['pc', 'instruction'])
    mt.append(headerrow)

    for cmsix in f:
        mtr = ET.Element('tr')
        mdname = ET.Element('td')
        if len(f[cmsix]['result']) == 0:
            mdname.text = f[cmsix]['methodstring']
        else:
            #mta = ET.Element('a')
            #mta.text = f[cmsix]['methodstring']
            mdname.text = f[cmsix]['methodstring']
            mdname.set('cmsix', cmsix)
            mdname.set('name', 'method')
            #linktxt = '/method/' + engagement + '/' + project + '/' + cmsix
            #mta.set('href', linktxt)
            #mta.set('target','_blank')
            #mdname.append(mta)
        mdname.set('colSpan', '2')
        mdname.set('style', 'border-style:none;')
        mtr.extend( [ mdname ] )
        mt.append(mtr) 
        for instr in f[cmsix]['result']:
            mtr = ET.Element('tr')
            tdindex = ET.Element('td')
            tdindex.text = instr[0]
            tdopcode = ET.Element('td')
            tdopcode.text = instr[1]
            mtr.extend([ tdindex, tdopcode ])
            mt.append(mtr)
        mtr = ET.Element('tr')
        empty = ET.Element('td')
        empty.text = u'\xa0'
        empty.set('colSpan', '2')
        empty.set('style', 'border-style:none;')
        mtr.append(empty)
        mt.append(mtr)

    table.append(mt)
    return table

def mk_header(labels: List[str]) -> ET.Element:
    headerrow = ET.Element('tr')
    for label in labels:
        header = ET.Element('th')
        button = ET.Element('button')
        button.text = label
        header.append(button)
        headerrow.append(header)
    return headerrow

def mk_method_code_table(f: List[List[str]]) -> ET.Element:
    table = ET.Element('div')
    table.set('id', 'codetable')
    mt = ET.Element('table')
    mt.set('class','methodtable balanced')

    headerrow = mk_header(['pc', 'instruction'])
    mt.append(headerrow)

    for line in f:
        mtr = ET.Element('tr')
        tdpc = ET.Element('td')
        tdpc.text = line[0]
        tdinstr = ET.Element('td')
        tdinstr.text = line[1]
        mtr.extend([ tdpc, tdinstr ])
        mt.append(mtr)
    table.append(mt)
    return table

def mk_display_body(mk_table, report):
    body = ET.Element('body')
    mainpage = ET.Element('div')
    mainpage.set('id','mainpage')
    header = ET.Element('header')
    header.text = 'CodeHawk Java Analyzer'
    nav = ET.Element('nav')
    navdiv  = ET.Element('div')
    navul = ET.Element('ul')
    navlihome = ET.Element('li')
    navlihome.text = 'HOME'
    navul.append(navlihome)
    navdiv.append(navul)
    nav.append(navdiv)
    codetable = mk_table(report)
    footer = ET.Element('footer')
    footer.text = '&copy; 2019-2020, Kestrel Technology, LLC, Palo Alto, CA 94304'
    mainpage.extend([ header, nav, codetable, footer ])
    body.append(mainpage)
    return body


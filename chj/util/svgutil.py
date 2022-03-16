# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
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

import os
import string
import subprocess
import difflib

import xml.etree.ElementTree as ET

import chj.util.dotutil as UD

from chj.util.DotGraph import DotGraph

from typing import List, Dict

def svg_namespace() -> Dict[str, str]:
    return {'svg' : 'http://www.w3.org/2000/svg'}

def _get_graph_nodes(svg: ET.ElementTree) -> List[ET.Element]:
    ns = svg_namespace()
    nodes = []
    elems = svg.findall('svg:g', namespaces=ns)
    for elem in elems:
        subelems = elem.findall('svg:g', namespaces=ns)
        for subelem in subelems:
            if subelem.attrib['class'] and subelem.attrib['class'] == 'node':
                nodes.append(subelem)
    return nodes

def append_loop_levels(svg: ET.ElementTree, loop_levels: Dict[int, int]) -> None:
    nodes = _get_graph_nodes(svg)
    for node in nodes:
        pc = int(node.attrib['pc'])
        node.attrib['ldepth'] = str(loop_levels[pc])

def append_cmsixs(svg: ET.ElementTree, cmsix_dict: Dict[str, str]) -> None:
    nodes = _get_graph_nodes(svg)
    for node in nodes:
        ns = svg_namespace()
        title = node.findtext('svg:title', namespaces=ns)
        if title in cmsix_dict:
            node.attrib['cmsix'] = str(cmsix_dict[title])

def append_pcs(svg: ET.ElementTree, node_pcs: Dict[str, int]) -> None:
    nodes = _get_graph_nodes(svg)
    for node in nodes:
        ns = svg_namespace()
        title = node.findtext('svg:title', namespaces=ns)
        if title in node_pcs:
            node.attrib['pc'] = str(node_pcs[title])

def save_svg(path: str, g: DotGraph) -> None:
    dotfilename = os.path.join(path, g.name + '.dot')
    svgfilename = os.path.join(path, g.name + '.svg')
    if os.path.isfile(dotfilename):
        cmd = [ 'dot', '-Tsvg', '-o', svgfilename, dotfilename ]
        subprocess.call(cmd, stderr=subprocess.STDOUT)

def get_svg(path: str, g: DotGraph) -> ET.ElementTree:
    graphsdir = os.path.join(path, 'graphs')
    if not os.path.isdir(graphsdir):
        os.mkdir(graphsdir)

    UD.save_dot(graphsdir, g)
    save_svg(graphsdir, g)

    svgfilename = os.path.join(graphsdir, g.name + '.svg')

    tree = ET.parse(svgfilename)

    #Removes the namespace prefixes from elements in the svg
    #This is necessary because HTML implicitly recognizes elements 
    #from the svg namespace but does not handle namespace prefixes
    ET.register_namespace("","http://www.w3.org/2000/svg")

    return tree


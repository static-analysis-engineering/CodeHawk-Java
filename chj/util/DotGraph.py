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

from typing import Dict, Tuple

#Dot specifies that " (double quotes) must be escaped
replacements = [ ('"', '\\"') ,
                     ('<init>', '\<init\>') ]

def sanitize(s: str) -> str:
    for (a,b) in replacements:
        s = s.replace(a,b)
    return s

class DotNode(object):

    def __init__(self,
        name: str,
        labeltxt: str=None,
        color: str=None,
        fillcolor: str=None,
        shaded: bool=False):
        self.name = name
        self.labeltxt = labeltxt
        self.shaded = shaded
        self.color = color
        self.fillcolor = fillcolor
        self.addquotes = True

    def set_label(self, s:str) -> None: self.labeltxt = sanitize(s)
    def set_color(self, c:str) -> None: self.color = c
    def set_fillcolor(self, c:str) -> None: self.fillcolor = c
    def set_shaded(self) -> None: self.shaded = True

    def __str__(self) -> str:
        quote = '"' if self.addquotes else ''
        if self.labeltxt is None:
            labeltxt = ''
        else:
            labeltxt = 'label="' + self.labeltxt + '"'

        if self.shaded:
            shadetxt = 'style=filled,color=".7 .3 1.0"'
        elif not self.color is None:
            shadetxt = 'style=filled,color="' + self.color + '"'
        elif not self.fillcolor is None:
            shadetxt = 'style=filled,fillcolor="' + self.fillcolor + '"'
        else:
            shadetxt = ''

        if len(labeltxt) == 0 and len(shadetxt) == 0:
            return (quote + self.name + quote)
        else:
            return (quote + self.name + quote + ' [' + labeltxt + ',' + shadetxt + '];')

class DotEdge(object):

    def __init__(self,
            src: str,
            tgt: str,
            labeltxt: str=None):
        self.src = src
        self.tgt = tgt
        self.bidirectional = False
        self.labeltxt = labeltxt
        self.addquotes = True

    def set_label(self,s:str) -> None: self.labeltxt = s

    def __str__(self) -> str:
        quote = '"' if self.addquotes else ''
        if self.labeltxt is None:
            attrs = ''
        else:
            attrs = ' [ label="' + self.labeltxt + '" ];'
        return (quote + self.src + quote + ' -> ' + quote + self.tgt + quote + attrs)
        

class DotGraph(object):

    def __init__(self,name: str) -> None:
        self.name = name
        self.nodes: Dict[str, DotNode] = {}
        self.edges: Dict[Tuple[str, str], DotEdge] = {}
        self.rankdir = 'TB'
        self.bgcolor = 'gray96'

    def add_node(self,
        name: str,
        labeltxt: str=None,
        shaded: bool=False,
        color: str=None,
        fillcolor: str=None) -> None:
        if not name in self.nodes:
            if not labeltxt is None: labeltxt = sanitize(labeltxt)
            self.nodes[name] = DotNode(name,labeltxt=labeltxt,shaded=shaded,color=color,fillcolor=fillcolor)

    def add_edge(self,
            src: str,
            tgt: str,
            labeltxt: str=None) -> None:
        self.add_node(src)
        self.add_node(tgt)
        if not (src,tgt) in self.edges:
            if not labeltxt is None: labeltxt = sanitize(labeltxt)
            self.edges[(src,tgt)] = DotEdge(src,tgt,labeltxt)

    def set_top_bottom(self) -> None: self.rankdir = 'TB'

    def __str__(self) -> str:
        lines = []
        lines.append('digraph ' + '"' + self.name + '" {')
        lines.append('edge [fontname="FreeSans",fontsize="12", ' +
                         'labelfontname="FreeSans",labelfontsize="12"]')
        lines.append('node [fontname="FreeSans",fontsize="14",shape="record"]')
        lines.append('rankdir=' + self.rankdir)
        lines.append('bgcolor=' + self.bgcolor)
        for n in self.nodes: lines.append(str(self.nodes[n]))
        for e in self.edges: lines.append(str(self.edges[e]))
        lines.append(' }')
        return '\n'.join(lines)
    

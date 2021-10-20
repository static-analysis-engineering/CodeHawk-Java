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

import hashlib

import xml.etree.ElementTree as ET

import chj.util.fileutil as UF

from chj.util.DotGraph import DotGraph

from typing import Callable, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.cost.MethodCost import MethodCost

class BBlock():
    '''Basic block in a method control flow graph.'''

    def __init__(self, cfg:"Cfg", xnode:ET.Element) -> None:
        self.cfg = cfg
        self.xnode = xnode
        self.hascondition = 'tcond' in self.xnode.attrib

    @property
    def firstpc(self) -> int:
        firstpc = self.xnode.get('first-pc')
        if firstpc is None:
            raise UF.CHJError('firstpc is missing from xml')
        else:
            return int(firstpc)

    @property
    def lastpc(self) -> int:
        lastpc = self.xnode.get('last-pc')
        if lastpc is None:
            raise UF.CHJError('lastpc is missing from xml')
        else:
            return int(lastpc)

    def get_loop_level_count(self) -> int: return len(self.get_loop_levels())

    def get_loop_levels(self) -> List[int]:
        if self.xnode.find('loop-levels') is None:
            return []
        return [ UF.safe_get(x, 'pc', 'pc missing from xml for loop in Basic Block at' + str(self.firstpc), int)
                    for x in UF.safe_find(self.xnode, 'loop-levels', 'loop-levels missing from xml for Basic Block at' + str(self.firstpc)).findall('level') ]

    def get_successor_loop_level_counts(self) -> List[int]:
        return [ x.get_loop_level_count() for x in self.get_successor_blocks() ]

    def get_successors(self) -> List[int]: return self.cfg.get_successors(self.firstpc)

    def get_successor_blocks(self) -> List["BBlock"]:
        return [ self.cfg.get_block(x) for x in self.get_successors() ]

    def get_tcond(self) -> str:
        if self.hascondition:
            return UF.safe_get(self.xnode, 'tcond', 'tcond missing from xml', str)
        else:
            raise UF.CHJError('tcond missing from xml')

    def get_fcond(self) -> str:
        if self.hascondition:
            return UF.safe_get(self.xnode, 'fcond', 'fcond missing from xml', str)
        else:
            raise UF.CHJError('fcond missing from xml')

    def has_conditions(self) -> bool:
        return ('tcond' in self.xnode.attrib)


class Cfg():
    '''Method control flow graph.'''

    def __init__(self, jmethod: "JavaMethod", xnode: ET.Element):
        self.jmethod = jmethod
        self.xnode = xnode
        self.blocks: Dict[int, BBlock] = {}            # firstpc -> BBlock
        self.edges: Dict[int, List[int]] = {}             # firstpc -> list of firstpcs
        self._initialize_blocks()
        self._initialize_edges()

    def get_block(self, pc: int) -> BBlock:
        if pc in self.blocks:
            return self.blocks[pc]
        else:
            raise UF.CHJError('No block found for pc = ' + str(pc))

    def get_loop_level_counts(self) -> Dict[int, int]:
        loop_levels = {}
        for pc in self.blocks:
            block = self.blocks[pc]
            loop_levels[pc] = block.get_loop_level_count()
        return loop_levels

    def get_successors(self, pc:int) -> List[int]:
        if pc in self.edges:
            return self.edges[pc]
        else:
            return []

    def iter_blocks(self, f: Callable[[BBlock], None]) -> None:
        for b in self.blocks: f(self.blocks[b])

    def cfg_hash(self) -> str:
        s = 'cfg'
        for src in sorted(self.edges):
            s += str(src)
            for tgt in sorted(self.edges[src]):
                s += str(tgt)
        h = hashlib.md5(s.encode('utf-8')).hexdigest()
        return h
        

    def enumerate_paths(self,
        startpc: int,
        endpc: int) -> List[List[int]]:
        def multiplicity(l:List[int], e:int) -> int:
            count = 0
            for x in l:
                if x == e: count += 1
            return count
        result: List[List[int]] = []
        prefix: List[int] = [ startpc ]
        def enumpaths(p: List[int]) -> None:
            prefix = p[:]
            lastpc = prefix[-1]
            succs = self.get_successors(lastpc)
            depth = 0
            if self.get_block(lastpc).get_loop_level_count() > 0:
                depth = 1
            for s in succs:
                if multiplicity(prefix,s) > depth: continue
                if s == endpc:
                    prefix.append(s)
                    result.append(prefix)
                    prefix = prefix[:-1]
                    break
            for s in succs:
                if (multiplicity(prefix,s) > depth) or s == endpc:
                    continue
                prefix.append(s)
                enumpaths(prefix)
                prefix = prefix[:-1]

        enumpaths(prefix)

        pathsets: List[Tuple[Set[int], int]] = []
        uniquepaths = []
        for p in result:
            if (set(p),len(p)) in pathsets: continue
            pathsets.append((set(p),len(p)))
            uniquepaths.append(p)
        return uniquepaths

    def _initialize_blocks(self) -> None:
        blockerrormsg = 'blocks missing from xml for ' + self.jmethod.get_name()
        firstpcerrormsg = 'blocks missing from xml for block in ' + self.jmethod.get_name()

        for b in UF.safe_find(self.xnode, 'blocks', blockerrormsg).findall('bblock'):
            self.blocks[ UF.safe_get(b, 'first-pc', firstpcerrormsg, int) ] = BBlock(self,b)

    def _initialize_edges(self) -> None:
        errormsg = ' missing from xml for ' + self.jmethod.get_name()

        for e in UF.safe_find(self.xnode, 'edges', 'edges ' + errormsg).findall('edge'):
            src = UF.safe_get(e, 'src', 'src' + errormsg, int)
            tgt = UF.safe_get(e, 'tgt', 'tgt' + errormsg, int)
            if not src in self.edges: self.edges[src] = []
            self.edges[src].append(tgt)

    def as_dot(self,
            methodcost: Optional["MethodCost"]=None,
            simplecost: bool=False) -> Tuple[Dict[str, int], DotGraph]:

        def register_node(nodes: Dict[str, int],
                            methodcost: Optional["MethodCost"],
                            dotgraph: DotGraph,
                            src: int,
                            simplecost: bool) -> str:
            if simplecost:
                srccost = " : " + str(methodcost.get_simplified_block_cost(src)) if methodcost else ""
            else:
                srccost = " : " + str(methodcost.get_block_cost(src)) if methodcost else ""
            srcstring = "pc=" + str(src) + srccost
            srcstring = srcstring.replace(' ', '').replace(u'\xa0', '')
            dotgraph.add_node(srcstring)
            nodes[srcstring] = src
            return srcstring

        def register_edge(nodes: Dict[str, int],
                            methodcost: Optional["MethodCost"],
                            dotgraph: DotGraph,
                            src: int,
                            simplecost: bool) -> str:
            if simplecost:
                srccost = " : " + str(methodcost.get_simplified_block_cost(src)) if methodcost else ""
            else:
                srccost = " : " + str(methodcost.get_block_cost(src)) if methodcost else ""
            srcstring = "pc=" + str(src) + srccost
            srcstring = srcstring.replace(' ', '').replace(u'\xa0', '')
            nodes[srcstring] = src
            return srcstring

        dotgraph = DotGraph("cfg_" + str(self.jmethod.cmsix))
        nodes: Dict[str, int] = {}

        for src in self.edges:
            block = self.get_block(src)
            if len(self.edges[src]) == 2 and block.has_conditions():
                labeltxt = ""

                srcstring = register_node(nodes, methodcost, dotgraph, src, simplecost)

                tgt = self.edges[src][0]
                blockstring = register_edge(nodes, methodcost, dotgraph, tgt, simplecost)
                dotgraph.add_edge(srcstring, blockstring, labeltxt=str(block.get_fcond()))

                tgt = self.edges[src][1]
                blockstring = register_edge(nodes, methodcost, dotgraph, tgt, simplecost)
                dotgraph.add_edge(srcstring, blockstring, labeltxt=str(block.get_tcond()))
            else:
                srcstring = register_node(nodes, methodcost, dotgraph, src, simplecost)

                for tgt in self.edges[src]:
                    blockstring = register_edge(nodes, methodcost, dotgraph, tgt, simplecost)
                    dotgraph.add_edge(srcstring, blockstring)

        for src in self.blocks:
            register_node(nodes, methodcost, dotgraph, src, simplecost)

        return (nodes, dotgraph)


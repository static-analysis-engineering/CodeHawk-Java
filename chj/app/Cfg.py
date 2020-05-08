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

from chj.util.DotGraph import DotGraph

class BBlock():
    '''Basic block in a method control flow graph.'''

    def __init__(self,cfg,xnode):
        self.cfg = cfg
        self.xnode = xnode
        self.firstpc = int(self.xnode.get('first-pc'))
        self.lastpc = int(self.xnode.get('last-pc'))
        self.hascondition = 'tcond' in self.xnode.attrib
        

    def get_loop_level_count(self): return len(self.get_loop_levels())

    def get_loop_levels(self):
        if self.xnode.find('loop-levels') is None:
            return []
        return [ int(x.get('pc')) for x in self.xnode.find('loop-levels').findall('level') ]

    def get_successor_loop_level_counts(self):
        return [ x.get_loop_level_count() for x in self.get_successor_blocks() ]

    def get_successors(self): return self.cfg.get_successors(self.firstpc)

    def get_successor_blocks(self):
        return [ self.cfg.get_block(x) for x in self.get_successors() ]

    def get_tcond(self):
        if self.hascondition: return self.xnode.get('tcond')

    def get_fcond(self):
        if self.hascondition: return self.xnode.get('fcond')

    def has_conditions(self): return ('tcond' in self.xnode.attrib)


class Cfg():
    '''Method control flow graph.'''

    def __init__(self,jmethod,xnode):
        self.jmethod = jmethod
        self.xnode = xnode
        self.blocks = {}            # firstpc -> BBlock
        self.edges = {}             # firstpc -> list of firstpcs
        self._initialize_blocks()
        self._initialize_edges()


    def get_block(self,pc):
        if pc in self.blocks:
            return self.blocks[pc]
        else:
            print('No block found for pc = ' + str(pc))

    def get_loop_level_counts(self):
        loop_levels = {}
        for pc in self.blocks:
            block = self.blocks[pc]
            loop_levels[pc] = block.get_loop_level_count()
        return loop_levels

    def get_successors(self,pc):
        if pc in self.edges:
            return self.edges[pc]
        else:
            return []

    def iter_blocks(self,f):
        for b in self.blocks: f(self.blocks[b])

    def cfg_hash(self):
        s = 'cfg'
        for src in sorted(self.edges):
            s += str(src)
            for tgt in sorted(self.edges[src]):
                s += str(tgt)
        h = hashlib.md5(s).hexdigest()
        return h
        

    def enumerate_paths(self,startpc,endpc):
        def multiplicity(l,e):
            count = 0
            for x in l:
                if x == e: count += 1
            return count
        result = []
        prefix = [ startpc ]
        def enumpaths(p):
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

        pathsets = []
        uniquepaths = []
        for p in result:
            if (set(p),len(p)) in pathsets: continue
            pathsets.append((set(p),len(p)))
            uniquepaths.append(p)
        return uniquepaths

    def _initialize_blocks(self):
        for b in self.xnode.find('blocks').findall('bblock'):
            self.blocks[ int(b.get('first-pc'))  ] = BBlock(self,b)

    def _initialize_edges(self):
        for e in self.xnode.find('edges').findall('edge'):
            src = int(e.get('src'))
            tgt = int(e.get('tgt'))
            if not src in self.edges: self.edges[src] = []
            self.edges[src].append(tgt)

    def as_dot(self, methodcost=None, simplecost=False):
        def register_node(nodes, methodcost, dotgraph, src, simplecost):
            if simplecost:
                srccost = " : " + str(methodcost.get_simplified_block_cost(src)) if methodcost else ""
            else:
                srccost = " : " + str(methodcost.get_block_cost(src)) if methodcost else ""
            srcstring = "pc=" + str(src) + srccost
            srcstring = srcstring.replace(' ', '').replace(u'\xa0', '')
            dotgraph.add_node(srcstring)
            nodes[srcstring] = src
            return srcstring

        def register_edge(nodes, methodcost, dotgraph, src, simplecost):
            if simplecost:
                srccost = " : " + str(methodcost.get_simplified_block_cost(src)) if methodcost else ""
            else:
                srccost = " : " + str(methodcost.get_block_cost(src)) if methodcost else ""
            srcstring = "pc=" + str(src) + srccost
            srcstring = srcstring.replace(' ', '').replace(u'\xa0', '')
            nodes[srcstring] = src
            return srcstring

        dotgraph = DotGraph("cfg_" + str(self.jmethod.cmsix))
        nodes = {}

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


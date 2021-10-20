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

import chj.util.printutil as UP

from typing import Any, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.app.JavaMethod import JavaMethod
    import chj.index.Taint as T

class LoopSummary(object):

    def __init__(self, app: "AppAccess", sources: List[int]=[]):
        self.app = app
        self.jd = app.jd
        self.sources = sources
        if sources is None:
            self.sources = []
        else:
            self.sources = [int(x) for x in sources]

    def as_dictionary(self) -> Dict[int, Dict[str, Any]]:
        results = {}
        for (cmsix, m) in self.app.get_methods():
            if m.get_loop_count() > 0:
                loops = m.get_loops()
                loopbounds = ','.join(l.get_bound() for l in loops)
                looptaints = self._get_loop_taints(m)
                loopresult = {}
                loopresult['loopcount'] = str(m.get_loop_count())
                loopresult['max-depth'] = str(m.get_max_depth())
                loopresult['loopbounds'] = loopbounds
                loopresult['looptaints'] = looptaints
                loopresult['aqname'] = m.get_aqname()
                results[cmsix] = loopresult
        return results

    def to_string(self) -> str:
        header = [ ('#loops',8), ('max-depth',14), ('bounds',14), ('taints',14) ]
        headerline = ''.join([ UP.cjust(str(t[0]),t[1]) for t in header ]) + ' method name (id)'
        result = []
        lines = []
        for (cmsix,m) in self.app.get_methods():
            if m.get_loop_count() > 0:
                loops = m.get_loops()
                loopbounds = ','.join(l.get_bound() for l in loops)
                looptaints = self._get_loop_taints(m)
                result.append((m.get_loop_count(),
                               m.get_max_depth(),
                               loopbounds,
                               looptaints,
                               m.get_aqname(),
                               m.cmsix))
        lines.append(headerline)
        lines.append('-' * 80)
        for t in sorted(result,key=lambda t:t[1],reverse=True):
            lines.append(UP.cjust(str(t[0]),8) +
                         UP.cjust(str(t[1]),14) +
                         UP.cjust(str(t[2]),14) +
                         UP.cjust(str(t[3]),14) +
                         str(t[4]) + ' (' + str(t[5]) + ')')
        return '\n'.join(lines)

    def list_to_string(self) -> str:
        lines = []
        header = [ ('entry-pc',8), ('   method',40), ('bound',14) ]
        headerline = '.'.join([ UP.cjust(t[0],t[1]) for t in header ])
        lines.append(headerline)
        lines.append('-' * 80)
        for (cmsix,m) in self.app.get_methods():
            if m.get_loop_count() > 0:
                loops = m.get_loops()
                for l in loops:
                    lines.append((str(l.first_pc).rjust(8) + '  ' +
                                  m.get_aqname().ljust(40) +
                                  str(l.get_bound()).rjust(14)))
        return '\n'.join(lines)

    def taint_list_to_string(self) -> str:
        result: Dict[int, List[Tuple["JavaMethod", int, int]]] = {}
        for (_, m) in self.app.get_methods():
            if m.get_loop_count() > 0:
                loops = m.get_loops()
                for l in loops:
                    depth = l.depth
                    pc = l.first_pc
                    lctaint = m.get_variable_taint('lc',pc)
                    if not lctaint is None:
                        untrusted = self.jd.gettaintoriginset(lctaint.getuntrustedtaint())
                        unknown = self.jd.gettaintoriginset(lctaint.getunknowntaint())
                        origins = set([x.getid() for x in untrusted.getorigins() +
                                           unknown.getorigins()])
                        for t in origins:
                            if t > 0 and (t in self.sources or len(self.sources) == 0):
                                if not t in result: result[t] = []
                                result[t].append((m,pc,depth))

        lines = []
        for t in result:
            taint = self.jd.get_taint_originsite(t)
            lines.append('\n' + str(t) + ': ' + str(taint))
            for (m,pc,depth) in sorted(result[t],
                                           key=lambda m,pc,depth:(depth,m.get_aqname()),reverse=True):
                lines.append('  ' + m.get_aqname() + ' @ ' + str(pc) + 
                ' (inner loops: ' + str(depth) + ')')
        return '\n'.join(lines)

    def taint_from_included_origin(self, tnode: "T.VariableTaintNode") -> bool:
        if len(self.sources) == 0: return True
        return tnode.index in self.sources
                                 

    def _get_target_sources(self, origins: List[int]) -> str:
        result = []
        for i in origins:
            if i in self.sources: result.append(str(i))
        if len(result) == 0:
            return('-')
        return ','.join(result)

    def _get_loop_taints(self, m: "JavaMethod") -> str:
        result = []
        for l in m.get_loops():
            lctaint = m.get_variable_taint('lc',l.first_pc)
            if (not lctaint is None) and self.taint_from_included_origin(lctaint):
                result.append('+')
            else:
                result.append('_')
        return ','.join(result)

    def looptaintstostring(self) -> None:
        for (_, m) in self.app.get_methods():
            if m.get_loop_count() > 0:
                sources = self._getlooptaintsources(m)
                if len(sources) > 0:
                    print('\n' + m.get_aqname())
                    for pc in sources:
                        print('  ' + str(pc))
                        for x in sources[pc]:
                            if x.getid() == 39 or x.getid() == 71:
                                print('    ' + str(x))

    def _getlooptaintsources(self, m: "JavaMethod") -> Dict[int, Any]:
        result: Dict[int, Any] = {}
        for l in m.get_loops():
            firstpc = l.first_pc
            lctaint = m.get_variable_taint('lc',firstpc)
            if not lctaint is None:
                untrusted = self.jd.get_taint_origin_set(lctaint.getuntrustedtaint())
                unknown = self.jd.get_taint_origin_set(lctaint.getunknowntaint())
                if untrusted.isempty() and unknown.isempty():
                    ()
                else:
                    result[firstpc] = []
                    result[firstpc].extend(untrusted.getorigins())
                    result[firstpc].extend(unknown.getorigins())
        return result
                    

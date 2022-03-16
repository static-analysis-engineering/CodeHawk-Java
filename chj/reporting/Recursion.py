# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma, Andrew McGraw
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

import chj.util.printutil as UP

from typing import Dict, List, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess
    from chj.index.CallgraphDictionary import CallgraphTargetBase

class Recursion():

    def __init__(self, app: "AppAccess"):
        self.app = app
        self.appedges: Dict[int, Set[int]] = self.get_appedges()    # cmsix -> targets

    def get_appedges(self) -> Dict[int, Set[int]]:
        jd = self.app.jd
        appedges: Dict[int, Set[int]] = {}

        def f(caller: int, pc: int, callee: int, tgt: "CallgraphTargetBase") -> None:
            if tgt.has_application_targets():
                if not caller in appedges: appedges[caller] = set([])
                cmstgts = [ jd.get_cmsix(cnix,callee) for cnix in tgt.get_application_targets() ]
                for c in cmstgts:
                    appedges[caller].add(c)

        jd.iter_callgraph_edges(f)
        return appedges

    def get_self_recursive_calls(self) -> List[int]:
        recursivecalls = []

        for caller in self.appedges:
            if caller in self.appedges[caller]:
                recursivecalls.append(caller)

        return recursivecalls

    def get_mutual_recursive_calls(self) -> Set[Tuple[int, int]]:
        mutualrecursivecalls = set([])

        for caller in self.appedges:
            callees = self.appedges[caller]
            for callee in callees:
                if callee in self.appedges and caller in self.appedges[callee]:
                    if callee == caller: continue
                    tuple = (caller,callee) if caller <= callee else (callee,caller)
                    mutualrecursivecalls.add(tuple)

        return mutualrecursivecalls

    def get_recursive_2_cycles(self) -> List[Tuple[int, int, int]]:
        recursive2cycles = []

        for caller in self.appedges:
            callees = self.appedges[caller]
            for callee in callees:
                if callee == caller: continue
                if callee in self.appedges:
                    subcallees = self.appedges[callee]
                    for subcallee in subcallees:
                        if subcallee in self.appedges and caller in self.appedges[subcallee]:
                            recursive2cycles.append((caller,callee,subcallee))
    
        return recursive2cycles

    def as_dictionary(self) -> Dict[str, List[Tuple[str, ...]]]:
        result: Dict[str, List[Tuple[str, ...]]] = {}
        jd = self.app.jd

        result["recursivecalls"] = [ (str(call), str(jd.get_cms(call))) for call in self.get_self_recursive_calls() ]
        result["mutualrecursivecalls"] = [ (str(caller), str(jd.get_cms(caller)), str(callee), str(jd.get_cms(callee)))
                                            for (caller, callee) in self.get_mutual_recursive_calls() ]
        result["recursive2cycles"] = [ (str(caller), str(jd.get_cms(caller)), str(callee),
                                            str(jd.get_cms(callee)), str(subcallee), str(jd.get_cms(subcallee)))
                                            for (caller, callee, subcallee) in self.get_recursive_2_cycles() ]

        return result

    def to_string(self) -> str:
        jd = self.app.jd

        lines = []

        lines.append('\nDirect recursion: ')
        for c in self.get_self_recursive_calls():
            lines.append(str(jd.get_cms(c)))
            

        lines.append('\nMutual recursion: ')
        for (caller,callee) in self.get_mutual_recursive_calls():
            caller_cms = jd.get_cms(caller)
            callee_cms = jd.get_cms(callee)
            lines.append('\n' + str(caller_cms) + '\n ==> ' + str(callee_cms))

        lines.append('\nCycle of 2: ')
        for (caller,callee,subcallee) in self.get_recursive_2_cycles():
            caller_cms = jd.get_cms(caller)
            callee_cms = jd.get_cms(callee)
            subcallee_cms = jd.get_cms(subcallee)
            lines.append('\n' + str(caller_cms) + '\n ==> ' + str(callee_cms) + '\n ====> ' + str(subcallee_cms))
            
        return '\n'.join(lines)

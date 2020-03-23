# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma, Andrew McGraw
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

class Recursion():

    def __init__(self,app):
        self.app = app
        self.appedges = self.get_appedges()    # cmsix -> targets

    def get_appedges(self):
        jd = self.app.jd
        appedges = {}

        def f(caller,pc,callee,tgt):
            if tgt.has_application_targets():
                if not caller in appedges: appedges[caller] = set([])
                cmstgts = [ jd.get_cmsix(cnix,callee) for cnix in tgt.get_application_targets() ]
                for c in cmstgts:
                    appedges[caller].add(c)

        jd.iter_callgraph_edges(f)
        return appedges

    def get_self_recursive_calls(self):
        recursivecalls = []

        for caller in self.appedges:
            if caller in self.appedges[caller]:
                recursivecalls.append(caller)

        return recursivecalls

    def get_mutual_recursive_calls(self):
        mutualrecursivecalls = set([])

        for caller in self.appedges:
            callees = self.appedges[caller]
            for callee in callees:
                if callee in self.appedges and caller in self.appedges[callee]:
                    if callee == caller: continue
                    tuple = (caller,callee) if caller <= callee else (callee,caller)
                    mutualrecursivecalls.add(tuple)

        return mutualrecursivecalls

    def get_recursive_2_cycles(self):
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

    def as_dictionary(self):
        result = {}
        jd = self.app.jd

        result["recursivecalls"] = [ (call, str(jd.get_cms(call))) for call in self.get_self_recursive_calls() ]
        result["mutualrecursivecalls"] = [ (caller, str(jd.get_cms(caller)), callee, str(jd.get_cms(callee))) 
                                            for (caller, callee) in self.get_mutual_recursive_calls() ]
        result["recursive2cycles"] = [ (caller, str(jd.get_cms(caller)), callee, 
                                            str(jd.get_cms(callee)), subcallee, str(jd.get_cms(subcallee))) 
                                            for (caller, callee, subcallee) in self.get_recursive_2_cycles() ]

        return result

    def to_string(self):
        jd = self.app.jd

        lines = []

        lines.append('\nDirect recursion: ')
        for c in self.get_self_recursive_calls():
            lines.append(str(jd.get_cms(c)))
            

        lines.append('\nMutual recursion: ')
        for (caller,callee) in self.get_mutual_recursive_calls():
            caller = jd.get_cms(caller)
            callee = jd.get_cms(callee)
            lines.append('\n' + str(caller) + '\n ==> ' + str(callee))

        lines.append('\nCycle of 2: ')
        for (caller,callee,subcallee) in self.get_recursive_2_cycles():
            caller = jd.get_cms(caller)
            callee = jd.get_cms(callee)
            subcallee = jd.get_cms(subcallee)
            lines.append('\n' + str(caller) + '\n ==> ' + str(callee) + '\n ====> ' + str(subcallee))
            
        return '\n'.join(lines)

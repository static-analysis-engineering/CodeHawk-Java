# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
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

from typing import Any, Callable, Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.index.AppAccess import AppAccess
    from chj.index.DataDictionary import DataDictionary
    from chj.index.MethodSignature import ClassMethodSignature
    from chj.cost.CostModel import CostModel
    from chj.cost.CostMeasure import CostMeasure
    from chj.cost.MethodCost import MethodCost

abbreviations = [
    ('com.cyberpointllc.stac.easydecision', 'ccse'),
    ('com.cyberpointllc.stac.webcontroller','ccsw'),
    ('com.cyberpointllc.stac', 'ccs'),
    ('com.google.protobuf','cgp'),
    ('java.lang.String','String'),
    ('java.lang.Class','Class'),
    ('java.lang.Object','Object'),
    ('java.util.Map','Map'),
    ('java.util.List','List'),
    ('java.util.Set','Set'),
    ('java.math.BigDecimal','BigDecimal'),
    ('java.math.BigInteger','BigInteger'),
    ('java.io.InputStream','InputStream'),
    ('java.io.OutputStream','OutputStream'),
    ('java.io.Reader','Reader'),
    ('java.io.Writer','Writer')
    ]


def abbreviatepackages(s: str) -> str:
    for (k,t) in abbreviations:
        s = s.replace(k,t)
    return s

class CostSummary(object):

    def __init__(self, app: "AppAccess"):
        self.app = app                  # AppAccess
        self.jd: "DataDictionary" = self.app.jd           # DataDictionary
        self.costmodel: "CostModel" = app.get_costmodel()
        self.constantcost: List[int] = []

    def get_cms(self, cmsix: int) -> "ClassMethodSignature": return self.jd.get_cms(cmsix)

    def get_range_cost_string(self) -> str:
        lines = []
        for (cmsix,(lb,ub)) in self.costmodel.get_range_method_costs():
            lines.append('[' + str(lb).rjust(8) + ' ; ' + str(ub).rjust(8) + ']  '
                             + str(self.get_cms(cmsix))
                             + ' (' + str(cmsix) + ')' )
        return '\n'.join(lines)

    def get_ranked_range_cost_string(self) -> str:
        '''ranked by ratio between lower bound and upper bound'''
        lines = []
        costs = self.costmodel.get_range_method_costs()
        lines.append('\n\nRange Cost: ' + str(len(costs)))
        rankedcosts = []
        for (cmsix,(lb,ub)) in costs:
            rankedcosts.append((cmsix,lb,ub,float(ub)/float(lb)))
        rankedcosts = sorted(rankedcosts,key=lambda x:x[3])
        for (cmsix,lb,ub,ratio) in rankedcosts:
            lines.append( '{:>5.1f}'.format(ratio).rjust(10) + '  [' + str(lb).rjust(8) + ' ; '
                              + str(ub).rjust(8) + '] '
                              + str(self.get_cms(cmsix))
                              + ' (' + str(cmsix) + ')')
        return '\n'.join(lines)

    def get_ranked_range_cost_dict(self) -> Dict[int, Tuple[str, str, str]]:
        cost_dict = {}
        costs = self.costmodel.get_range_method_costs()

        rankedcosts = []
        for (cmsix, (lb, ub)) in costs:
            rankedcosts.append((cmsix,lb,ub,float(ub)/float(lb)))
        rankedcosts = sorted(rankedcosts,key=lambda x:x[3])
        for (cmsix,lb,ub,ratio) in rankedcosts:
            name = str(self.get_cms(cmsix)) + ' (' + str(cmsix) + ')'
            cost_dict[cmsix] = (name, str(lb), str(ub))
        return cost_dict

    def has_calls(self, cmsix: int) -> bool:
        return self.app.get_method(cmsix).has_calls()

    def get_call_targets(self, cmsix: int) -> List[int]:
        return self.app.get_method(cmsix).get_callee_cmsixs()

    def as_dictionary(self) -> Dict[str, Dict[int, Any]]:
        costs: Dict[str, Dict[int, Any]] = {}

        topmethodcosts = self.costmodel.get_top_method_costs()
        costs['topcosts'] = {}
        topcosts = costs['topcosts']
        for cmsix in topmethodcosts:
            name = str(self.get_cms(cmsix)) + ' (' + str(cmsix) + ')'
            topcosts[cmsix] = (name, 'Top')

        constantmethodcosts = self.costmodel.get_constant_method_costs()
        costs['constantcosts'] = {}
        constantcosts = costs['constantcosts']
        for (cmsix,cost) in constantmethodcosts:
            name = str(self.get_cms(cmsix)) + ' (' + str(cmsix) + ')'
            if (not self.has_calls(cmsix)):
                pcalls = ' (*)  '
                self.constantcost.append(cmsix)
            else:
                tgts = self.get_call_targets(cmsix)
                if all( c in self.constantcost for c in tgts):
                    pcalls = ' (**) '
                    self.constantcost.append(cmsix)
                else:
                    pcalls = '      '
            constantcosts[cmsix] = (name, str(cost).rjust(10) + pcalls)

        costs['rangecosts'] = self.get_ranked_range_cost_dict()

        return costs


    def to_string(self,
            allcosts: bool=True, 
            namefilter: Callable[[str], bool]=(lambda name:True)) -> str:
        lines = []

        topmethodcosts = self.costmodel.get_top_method_costs()
        lines.append('\n\nCost is Top: ' + str(len(topmethodcosts)) )
        for cmsix in topmethodcosts:
            name = str(self.get_cms(cmsix))
            if namefilter(name):
                lines.append('  ' + str(self.get_cms(cmsix)) + ' (' + str(cmsix) + ')')

        constantmethodcosts = self.costmodel.get_constant_method_costs()
        lines.append('\n\nConstant Cost: ' + str(len(constantmethodcosts)))
        for (cmsix,cost) in constantmethodcosts:
            name = str(self.get_cms(cmsix))
            if namefilter(name):
                if (not self.has_calls(cmsix)):
                    pcalls = ' (*)  '
                    self.constantcost.append(cmsix)
                else:
                    tgts = self.get_call_targets(cmsix)
                    if all( c in self.constantcost for c in tgts):
                        pcalls = ' (**) '
                        self.constantcost.append(cmsix)
                    else:
                        pcalls = '      '
                lines.append(str(cost).rjust(10) + pcalls + str(self.get_cms(cmsix))
                                + ' (' + str(cmsix) + ')')

        lines.append(self.get_ranked_range_cost_string())

        if allcosts:
            symbolicdeps: Dict[int, int] = {}
            multipledeps: Dict[str, int] = {}
            symboliccosts = self.costmodel.get_symbolic_method_costs()
            lines.append('\n\nSymbolic cost expressions: ' + str(len(symboliccosts)))
            for (cmsix, symcost) in symboliccosts:
                name = str(self.get_cms(cmsix))
                if namefilter(name):
                    lines.append('\n' + str(self.get_cms(cmsix))
                                    + ' (' + str(cmsix) + ')')
                    lines.append('   ' + str(symcost))
                    lines.append('symbolic dependencies:')
                    for j in symcost.get_ub_symbolic_dependencies():
                        depsname = j.get_name().split('_')
                        symbolicname = ''
                        symboliccost = '?'
                        if len(depsname) == 2:
                            cmsix = int(depsname[1])
                            if not cmsix in symbolicdeps: symbolicdeps[cmsix] = 0
                            symbolicdeps[cmsix] += 1
                            symbolicname = str(self.jd.get_cms(cmsix))
                            #symboliccost = str(self.costmodel.get_method_cost(cmsix))
                        elif len(depsname) > 2 and not 'lc' in depsname and 'pc' in depsname:
                            jname = '_'.join(j.get_name().split('_')[:-2])
                            multipledeps.setdefault(jname,0)
                            multipledeps[jname] += 1
                        lines.append('   ' + str(j) + '  ' + symbolicname)
                        # if (not (symboliccost is None)) and symboliccost != '?':
                        #    lines.append('      --> (' + str(symboliccost.methodcost)  + ')')

            unknowncosts = len(symbolicdeps)
            affected = sum( [ symbolicdeps[i] for i in symbolicdeps ])
            lines.append('\nMethods with unknown cost (' + str(unknowncosts) + ', '
                             + str(affected) + ')')
            for cmsix in sorted(symbolicdeps):
                cms = self.jd.get_cms(cmsix)
                cmscount = symbolicdeps[cmsix]
                lines.append(str(cmsix).rjust(4) + '  ' + str(cmscount).rjust(4) + '  '
                                        + str(cms))

            multipledepcount = len(multipledeps)
            affected = sum( [ multipledeps[i] for i in multipledeps ])
            lines.append('\nAmbiguity in method resolution ('
                             + str(len(multipledeps)) + ', '
                             + str(affected) + ')')
            for j in sorted(multipledeps):
                depsname = j.split('_')
                lines.append(j + ' (' + str(multipledeps[j]) + ')')
                for d in depsname[1:]:
                    if d in  [ 'funcall', 'no', 'callees', '', 'pc' ]:
                        continue
                    else:
                        cmsix = int(d)
                        cmsname = str(self.jd.get_cms(cmsix))
                        lines.append('  - ' + cmsname)


        sclines = [ abbreviatepackages(s) for s in lines ]
        return '\n'.join(sclines)

    def to_verbose_string(self, namefilter: Callable[[str], bool]=(lambda name:True)) -> str:
        lines = []
        lines.append('\n\nMethods')
        lines.append('-' * 80)
        def f(mc):
            name = str(self.get_cms(mc.cmsix))
            if not namefilter(name): return
            if mc.methodcost.is_value(): return
            lines.append('\n' + mc.get_qname() + ' (' + str(mc.cmsix) + '): '
                             + str(mc.methodcost.cost.get_upper_bounds()))
            for (pc,bc) in sorted(mc.get_block_costs()):
                lines.append(str(pc).rjust(8) + '  ' + str(bc))
        self.costmodel.iter(f)
        return '\n'.join(lines)

    def to_loop_bounds_string(self) -> str:
        result: Dict[int, Dict[int, Tuple["CostMeasure", "CostMeasure"]]] = {}
        lines = []
        def f(mc: "MethodCost") -> None:
            loopcosts = mc.get_loop_costs()
            if len(loopcosts) > 0:
                for l in loopcosts:
                    cmsix = mc.cmsix
                    if not cmsix in result: result[cmsix] = {}
                    result[cmsix][l.pc] = (l.one_iteration_cost,l.iteration_count)
        self.costmodel.iter(f)
        for cmsix in sorted(result):
            lines.append('\n' + str(self.get_cms(cmsix)) + ' (' + str(cmsix) + ')')
            for pc in sorted(result[cmsix]):
                (it,num) = result[cmsix][pc]
                lines.append('  pc=' + str(pc))
                lines.append('   1-it: ' + str(it))
                lines.append('   n-it: ' + str(num))
        return '\n'.join(lines)

    def to_side_channels_string(self) -> str:
        lines = []
        def f(mc):
            if mc.has_sidechannel_checks():
                lines.append('\n' + mc.get_qname() + ' (' + str(mc.cmsix) + ')')
                for sc in mc.sidechannelchecks:
                    lines.append(str(sc))
        self.costmodel.iter(f)
        if len(lines) > 0:
            lines = [ '\nSide channel checks:', '-' * 80 ] + lines
        return '\n'.join(lines)

                         

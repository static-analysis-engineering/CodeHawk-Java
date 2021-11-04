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

from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess

class StaticFields():

    def __init__(self, app: "AppAccess"):
        self.app = app
        self.initializers = self.app.get_static_initializers()
        self.readers = self.app.get_static_field_readers()

    def as_dictionary(self) -> Dict[str, Dict[str, Dict[str, Dict[int, Tuple[int, str]]]]]:
        results = {}
        initdict: Dict[str, Dict[str, Dict[int, Tuple[int, str]]]] = {}
        readerdict: Dict[str, Dict[str, Dict[int, Tuple[int, str]]]] = {}
        for (cmsix, minitializers) in self.initializers:
            cms = str(self.app.jd.get_cms(cmsix).get_aqname())
            for (pc,cn,field) in minitializers:
                cnix = str(self.app.jd.get_cn(cn.index))
                fsix = str(self.app.jd.get_fs(field.index))
                if not cnix in initdict: initdict[cnix] = {}
                if not fsix in initdict[cnix]: initdict[cnix][fsix] = {}
                initdict[cnix][fsix][cmsix] = (pc, cms)

        for (cmsix, mreaders) in self.readers:
            cms = str(self.app.jd.get_cms(cmsix).get_aqname())
            for (pc,cn,field) in mreaders:
                cnix = str(self.app.jd.get_cn(cn.index))
                fsix = str(self.app.jd.get_fs(field.index))
                if not cnix in readerdict: readerdict[cnix] = {}
                if not fsix in readerdict[cnix]: readerdict[cnix][fsix] = {}
                readerdict[cnix][fsix][cmsix] = (pc, cms)

        results['initdict'] = initdict
        results['readerdict'] = readerdict
        return results

    def to_string(self) -> str:
        lines = []

        initdict: Dict[int, Dict[int, List[Tuple[int, int]]]] = {}
        readerdict: Dict[int, Dict[int, List[Tuple[int, int]]]] = {}
        for (cmsix,minitializers) in self.initializers:
            for (pc,cn,field) in minitializers:
                cnix = cn.index
                fsix = field.index
                if not cnix in initdict: initdict[cnix] = {}
                if not fsix in initdict[cnix]: initdict[cnix][fsix] = []
                initdict[cnix][fsix].append((cmsix,pc))
            
        for (cmsix,mreaders) in self.readers:
            for (pc,cn,field) in mreaders:
                cnix = cn.index
                fsix = field.index
                if not cnix in readerdict: readerdict[cnix] = {}
                if not fsix in readerdict[cnix]: readerdict[cnix][fsix] = []
                readerdict[cnix][fsix].append((cmsix,pc))

        for cnix in sorted(initdict):
            lines.append('\n')
            lines.append('-' * 80)
            lines.append((str(self.app.jd.get_cn(cnix))))
            lines.append('-' * 80)
            for fsix in sorted(initdict[cnix]):
                lines.append('\n  ' + str(self.app.jd.get_fs(fsix)))
                lines.append('  initializers:')
                for (cmsix,pc) in initdict[cnix][fsix]:
                    lines.append(str(pc).rjust(6) + '  '
                                     + self.app.jd.get_cms(cmsix).get_aqname())
                lines.append('\n  readers:')
                if cnix in readerdict and fsix in readerdict[cnix]:
                    for (cmsix,pc) in readerdict[cnix][fsix]:
                        lines.append(str(pc).rjust(6) + '  '
                                         + self.app.jd.get_cms(cmsix).get_aqname())
        return '\n'.join(lines)


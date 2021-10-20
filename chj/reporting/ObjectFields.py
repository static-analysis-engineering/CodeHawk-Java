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

from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess

class ObjectFields():

    def __init__(self, app: "AppAccess"):
        self.app = app
        self.fieldwriters = self.app.get_object_field_writers()
        self.fieldreaders = self.app.get_object_field_readers()

    def to_string(self) -> str:
        lines = []
        dictwriters: Dict[int, Dict[int, List[Tuple[int, int]]]] = {}
        dictreaders: Dict[int, Dict[int, List[Tuple[int, int]]]] = {}
        for (cmsix,mwriters) in self.fieldwriters:
            for (pc,cn,field) in mwriters:
                cnix = cn.index
                fsix = field.index
                if not cnix in dictwriters: dictwriters[cnix] = {}
                if not fsix in dictwriters[cnix]: dictwriters[cnix][fsix] = []
                dictwriters[cnix][fsix].append((cmsix,pc))
            
        for (cmsix,mreaders) in self.fieldreaders:
            for (pc,cn,field) in mreaders:
                cnix = cn.index
                fsix = field.index
                if not cnix in dictreaders: dictreaders[cnix] = {}
                if not fsix in dictreaders[cnix]: dictreaders[cnix][fsix] = []
                dictreaders[cnix][fsix].append((cmsix,pc))

        for cnix in sorted(dictwriters):
            lines.append(('\n' + str(self.app.jd.get_cn(cnix))))
            for fsix in sorted(dictwriters[cnix]):
                lines.append('\n  ' + str(self.app.jd.get_fs(fsix)))
                lines.append('  writers:')
                for (cmsix,pc) in dictwriters[cnix][fsix]:
                    lines.append(str(pc).rjust(6) + '  '
                                     + self.app.jd.get_cms(cmsix).get_aqname())
                lines.append('\n  readers:')
                if cnix in dictreaders and fsix in dictreaders[cnix]:
                    for (cmsix,pc) in dictreaders[cnix][fsix]:
                        lines.append(str(pc).rjust(6) + '  '
                                         + self.app.jd.get_cms(cmsix).get_aqname())
        return '\n'.join(lines)


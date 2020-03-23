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

import argparse
import os

import chj.util.printutil as UP
import chj.util.fileutil as UF

from chj.index.AppAccess import AppAccess

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('--multiple',action='store_true',help='only show callsites with multiple targets')
    args = parser.parse_args()
    return args

def multiple(cmsedges):
    for pc in cmsedges:
        tgt = cmsedges[pc]
        if tgt.is_virtual_target() and tgt.get_length() > 1:
            return True
    else:
        return False

if __name__ == '__main__':

    args = parse()
    
    try:
        (path,_) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    app = AppAccess(path)
    callgraph = app.get_callgraph()

    for cmsix in callgraph.edges:
        cmsedges = callgraph.edges[cmsix]
        cms = app.jd.get_cms(cmsix)
        if multiple(cmsedges) or (not args.multiple):
            print('\n' + str(cms) + ' (' + str(cmsix) + ')')
            for pc in sorted(cmsedges):
                tgt = cmsedges[pc]
                if (not args.multiple) or (tgt.is_virtual_target() and tgt.get_length() > 1):
                    print('  ' + str(pc).rjust(4) + ': ' + str(cmsedges[pc]))



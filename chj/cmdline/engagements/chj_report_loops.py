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
"""Reports the presence of loops in an Engagement application."""

import argparse
import os

import chj.util.printutil as UP
import chj.util.fileutil as UF

from chj.index.AppAccess import AppAccess
from chj.reporting.LoopSummary import LoopSummary

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('--taintorigins',nargs='*',type=int,
                            help='only include taint from given origins (default: all)')
    parser.add_argument('--save',help='save report to chreports directory',action='store_true')
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse()

    try:
        (path,_) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    taintorigins = []
    if not args.taintorigins is None: taintorigins = args.taintorigins

    taintnodes = []

    app = AppAccess(path)
    for t in taintorigins:
        xnode = UF.get_data_taint_trail_xnode(path,int(t))
        if xnode is None:
            print('No taint trail found for id ' + str(t))
            exit(1)
        dnode = xnode.find('node-dictionary')
        for n in dnode.findall('tn'):
            taintnodes.append(int(n.get('ix')))

    lines = []
    headername = args.appname
    lines.append(UP.reportheader('Loop Summary',headername))
    loopsummary = LoopSummary(app,sources=list(taintnodes))
    if len(taintorigins) > 0:
        for tn in taintorigins:
            lines.append(str(tn).rjust(4) + '  '
                             + str(app.jd.ttd.get_taint_origin(tn)))
        lines.append('-' * 80)
    lines.append(loopsummary.to_string())
    lines.append('\n\n')
    lines.append(loopsummary.list_to_string())

    if args.save:
        reportsdir = UF.get_engagement_reports_dir(path)
        if reportsdir is None:
            print('*' * 80)
            print('Unable to create reports directory')
            print('*' * 80)
            exit(1)
        filename = os.path.join(reportsdir,'loops_report.txt')
        with open(filename,'w') as fp:
            fp.write('\n'.join(lines))
    else:
        print('\n'.join(lines))
    

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
"""Reports the cpu time cost of methods annd loops."""

import argparse

import chj.util.printutil as UP
import chj.util.fileutil as UF

from chj.index.AppAccess import AppAccess
from chj.reporting.CostSummary import CostSummary

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('--verbose',help='include block costs',action='store_true')
    parser.add_argument('--loops',help='include loop body costs and bound values',action='store_true')
    parser.add_argument('--save',help='save report to chreports directory',action='store_true')
    parser.add_argument('--namerestriction',nargs='*',
                            help='only report functions that contain these as substrings')
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

    app = AppAccess(path)
    costreport = CostSummary(app)

    if not args.namerestriction is None:
        def namefilter(name):
            for n in args.namerestriction:
                if not n in name:
                    return False
            return True
    else:
        namefilter = lambda name:True

    lines = []
    headername = args.appname
    lines.append(UP.reportheader('Cost Model Summary',headername))
    lines.append(costreport.to_string(namefilter=namefilter))
    lines.append(costreport.to_side_channels_string())
    if args.verbose: lines.append(costreport.to_verbose_string())
    if args.loops: lines.append(costreport.to_loop_bounds_string())

    if args.save:
        reportsdir = UF.get_engagement_reports_dir(path)
        if reportsdir is None:
            print('*' * 80)
            print('Unable to create reports directory')
            print('*' * 80)
            exit(1)
        filename = os.path.join(reportsdir,'cost_model_report.txt')
        with open(filename,'w') as fp:
            fp.write('\n'.join(lines))
    else:
        print('\n'.join(lines))


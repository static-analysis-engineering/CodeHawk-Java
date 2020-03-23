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
"""Prints out the sources of taint in an engagement application."""

import argparse

import chj.util.fileutil as UF
import chj.util.printutil as UP

from chj.index.AppAccess import AppAccess
from chj.reporting.TaintOrigins import TaintOrigins

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('appname',help='name of engagement application')
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

    app = AppAccess(path)

    lines = []
    headername = args.appname
    lines.append(UP.reportheader('Taint Origins',headername))
    lines.append(TaintOrigins(app).tostring())

    if args.save:
        reportsdir = UF.get_engagement_reports_dir(path)
        if reportsdir is None:
            print('*' * 80)
            print('Unable to create reports directory')
            print('*' * 80)
            exit(1)
        filename = os.path.join(reportsdir,'taint_origins_report.txt')
        with open(filename,'w') as fp:
            fp.write('\n'.join(lines))
    else:
        print('\n'.join(lines))
    


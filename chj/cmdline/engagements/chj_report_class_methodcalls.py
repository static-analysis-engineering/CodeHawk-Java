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

import chj.util.fileutil as UF
import chj.util.printutil as UP

from chj.index.AppAccess import AppAccess

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('classname',help='name of the target class of a method')
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
    lines.append(UP.reportheader('Named method calls to ' + args.classname,headername))

    results = []
    def f(cmsix,m):
        results.append((cmsix,m.get_class_method_calls(args.classname)))
    app.iter_methods(f)

    for (cmsix,mmethodcalls) in results:
        if len(mmethodcalls) > 0:
            lines.append('\n'+ app.jd.get_cms(cmsix).get_aqname())
            for (pc,i) in mmethodcalls:
                loopdepth = i.get_loop_depth()
                loopdepth = 'L' + str(loopdepth) if loopdepth > 0 else '  '
                lines.append(str(pc).rjust(6) + '  ' + loopdepth + '  ' + str(i))

    if args.save:
        reportsdir = UF.get_engagement_reports_dir(path)
        if reportsdir is None:
            print('*' * 80)
            print('Unable to create reports directory')
            print('*' * 80)
            exit(1)
        filename = 'method_calls_to_' + args.classname + '.txt'
        filename = os.path.join(reportsdir,filename)
        with open(filename,'w') as fp:
            fp.write('\n'.join(lines))
    else:
        print('\n'.join(lines))


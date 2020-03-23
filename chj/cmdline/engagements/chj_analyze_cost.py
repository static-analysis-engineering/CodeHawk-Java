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
"""Runs the CodeHawk Java analyzer on an engagement application to create a cost model."""

import argparse

import chj.cmdline.AnalysisManager as AM
import chj.util.fileutil as UF

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('--space',help='analyze for space cost',action='store_true')
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse()
    
    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)
    
    pkg_excludes = UF.get_engagement_app_excludes(args.appname)
    dependencies = UF.get_engagement_app_dependencies(args.appname)

    try:
        am = AM.AnalysisManager(path,jars,platform="ref_8.0_121",
                                    dependencies=dependencies,excludes=pkg_excludes)
        am.create_cost_model(space=args.space)
    except UF.CHJError as e:
        print(str(e.wrap()))
        

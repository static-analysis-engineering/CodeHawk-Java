# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Andrew McGraw
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2021 Andrew McGraw
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

import chj.util.fileutil as UF
import chj.cmdline.AnalysisManager as AM
import chj.cmdline.commandutils as UCC

from contextlib import contextmanager

from typing import NoReturn

def analyze(args: argparse.Namespace) -> NoReturn:
    app: str = args.appname

    try:
        UF.check_analyzer()
        (path, jars) = UF.get_engagement_app_jars(args.appname)
        UF.remove_analysis_dir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit()

    pkg_excludes = UF.get_engagement_app_excludes(args.appname)
    dependencies = UF.get_engagement_app_dependencies(args.appname)

    print('Analyzing: ' + args.appname + ' (' + path + ')')

    with UCC.timing('numerical analysis'):
        try:
            am = AM.AnalysisManager(path, jars, platform='ref_8.0_121',
                                    dependencies=dependencies,excludes=pkg_excludes)
            am.analyze(False)
        except UF.CHJError as e:
            print(str(e.wrap()))
    exit(0)

def analyze_cost(args: argparse.Namespace) -> NoReturn:
    app: str = args.appname

    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    pkg_excludes = UF.get_engagement_app_excludes(args.appname)
    dependencies = UF.get_engagement_app_dependencies(args.appname)

    with UCC.timing('cost analysis'):
        try:
            am = AM.AnalysisManager(path,jars,platform="ref_8.0_121",
                                    dependencies=dependencies,excludes=pkg_excludes)
            am.create_cost_model(space=False)
        except UF.CHJError as e:
            print(str(e.wrap()))
    exit(0)

def analyze_taint(args: argparse.Namespace) -> NoReturn:
    app: str = args.appname

    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    pkg_excludes = UF.get_engagement_app_excludes(args.appname)
    dependencies = UF.get_engagement_app_dependencies(args.appname)

    with UCC.timing('taint analysis'):
        try:
            am = AM.AnalysisManager(path,jars,platform="ref_8.0_121",
                                        dependencies=dependencies,excludes=pkg_excludes)
            am.create_taint_graphs(space=args.space)
        except UF.CHJError as e:
            print(str(e.wrap()))
    exit(0)

def analyze_taint_propagation(args: argparse.Namespace) -> NoReturn:
    app: str = args.appname
    origin: int = args.origin

    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    pkg_excludes = UF.get_engagement_app_excludes(args.appname)
    dependencies = UF.get_engagement_app_dependencies(args.appname)

    am = AM.AnalysisManager(path,jars,dependencies=dependencies,excludes=pkg_excludes)

    with UCC.timing('taint propagation analysis'):
        try:
            am.create_taint_trail(args.origin)
        except UF.CHJError as e:
            print(str(e.wrap()))
    exit(0)


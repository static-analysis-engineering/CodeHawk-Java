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

import argparse, os, time

from contextlib import contextmanager

import chj.cmdline.AnalysisManager as AM
import chj.util.fileutil as UF

from typing import List, Iterator, NoReturn

@contextmanager
def timing(activity: str) -> Iterator[None]:
    t0 = time.time()
    yield
    print('\n' + ('=' * 80) +
          '\nCompleted ' + activity + ' in ' + str(time.time() - t0) + ' secs' +
          '\n' + ('=' * 80))

def check_app_analysisdir(app: str) -> str:
    try:
        (path,_) = UF.get_engagement_app_jars(app)
        UF.check_analysisdir(path)
        return path
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

def save(path: str, outputfile: str, lines: List[str]) -> None:
    reportsdir = UF.get_engagement_reports_dir(path)
    if reportsdir is None:
        print('*' * 80)
        print('Unable to create reports directory')
        print('*' * 80)
        exit(1)
    filename = os.path.join(reportsdir, outputfile)
    with open(filename, 'w') as fp:
        fp.write('\n'.join(lines))

def scan(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    showmissingclasses: bool = args.showmissingclasses
    showmissingmethods: bool = args.showmissingmethods
    platform_independent: bool = args.platform_independent

    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.remove_analysis_dir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    pkg_excludes = UF.get_engagement_app_excludes(appname)
    dependencies = UF.get_engagement_app_dependencies(appname)

    print('Scanning: ' + appname + ' (' + path + ')')

    platform = None if platform_independent else "ref_8.0_121"

    try:
        am = AM.AnalysisManager(path,jars,platform=platform,
                                    dependencies=dependencies,excludes=pkg_excludes)
        am.scanonly()
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    if len(am.missinglibraries) > 0:
        print('=' * 80)
        print('Missing libraries:')
        for d in am.missinglibraries:
            print('  ' + d)
        print('=' * 80)

    xmissingitems = UF.get_datamissingitems_xnode(path)
    missingclasses = []
    missingmethods = []
    missingfields = []

    def missing_items_to_string(name: str, items: List[str]) -> str:
        lines = []
        lines.append('=' * 80)
        lines.append('Missing ' + name + ' (' + str(len(items)) +  ')')
        for i in items:
            lines.append('  ' + i)
        lines.append('=' * 80)
        return '\n'.join(lines)

    for c in UF.safe_find(xmissingitems, 'missing-classes', 'missing-classes missing from xml').findall('cn'):
        missingclasses.append(UF.safe_get(c, 'name', 'name missing from xml', str))

    if showmissingclasses:
        if len(missingclasses) > 0:
            print(missing_items_to_string('classes',missingclasses))

    if showmissingmethods:
        for m in UF.safe_find(xmissingitems, 'missing-methods', 'missing-methods missing from xml').findall('method'):
            missingmethods.append(UF.safe_get(m, 'str', 'str missing from xml', str))

        if len(missingmethods) > 0:
            print(missing_items_to_string('methods',missingmethods))

    for f in UF.safe_find(xmissingitems, 'missing-fields', 'missing-fields missing from xml').findall('field'):
        missingfields.append(UF.safe_get(f, 'name', 'name missing from xml', str))

    if len(missingfields) > 0:
        print(missing_items_to_string('fields',missingfields))
    exit(0)

def translate(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname

    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.remove_analysis_dir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    pkg_excludes = UF.get_engagement_app_excludes(appname)
    dependencies = UF.get_engagement_app_dependencies(appname)

    am = AM.AnalysisManager(path,jars,dependencies=dependencies,excludes=pkg_excludes)
    try:
        am.translate_only()
    except UF.CHJError as e:
        print(str(e.wrap()))
    exit(0)

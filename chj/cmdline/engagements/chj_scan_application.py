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
"""Parses an Engagement application and extracts some statistics."""

import argparse
import os
import subprocess

from chj.util.Config import Config

import chj.cmdline.AnalysisManager as AM
import chj.util.fileutil as UF

def parse():
    usage = ('invoke with the name of an Engagement application, e.g., blogger')
    parser = argparse.ArgumentParser(usage=usage,description=__doc__)
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('--showmissingclasses','-c',action='store_true',
                            help='show list of missinng classes')
    parser.add_argument('--showmissingmethods','-m',action='store_true',
                            help='show list of missing methods')
    parser.add_argument('--platform_independent','-i',action='store_true',
                            help="don't use reference platform")
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse()

    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.remove_analysis_dir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    pkg_excludes = UF.get_engagement_app_excludes(args.appname)
    dependencies = UF.get_engagement_app_dependencies(args.appname)

    print('Scanning: ' + args.appname + ' (' + path + ')')

    platform = None if args.platform_independent else "ref_8.0_121"

    try:
        am = AM.AnalysisManager(path,jars,platform=platform,
                                    dependencies=dependencies,excludes=pkg_excludes)
        result = am.scanonly()
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

    def missing_items_to_string(name,items):
        lines = []
        lines.append('=' * 80)
        lines.append('Missing ' + name + ' (' + str(len(items)) +  ')')
        for i in items:
            lines.append('  ' + i)
        lines.append('=' * 80)
        return '\n'.join(lines)

    for c in xmissingitems.find('missing-classes').findall('cn'):
        missingclasses.append(c.get('name'))

    if args.showmissingclasses:
        if len(missingclasses) > 0:
            print(missing_items_to_string('classes',missingclasses))
            
    if args.showmissingmethods:
        for m in xmissingitems.find('missing-methods').findall('method'):
            missingmethods.append(m.get('name'))

        if len(missingmethods) > 0:
            print(missing_items_to_string('methods',missingmethods))

    for f in xmissingitems.find('missing-fields').findall('field'):
        missingfields.append(f.get('name'))

    if len(missingfields) > 0:
        print(missing_items_to_string('fields',missingfields))

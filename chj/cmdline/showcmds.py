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

import argparse, os, sys

import chj.util.fileutil as UF
import chj.cmdline.AnalysisManager as AM
import chj.cmdline.commandutils as UCC

from chj.index.AppAccess import AppAccess
import chj.reporting.BytecodeReport as BRP

from contextlib import contextmanager

from typing import Dict, List, NoReturn, Tuple

def show_times(args: argparse.Namespace) -> NoReturn:
    engagement: str = args.engagement

    appdata = UF.get_engagements_data_file()[engagement]['apps']

    maxlen = max([ len(app) for app in appdata ] ) + 2

    print('application'.ljust(maxlen) + 'methods'.rjust(10) + 'analysis time (secs)'.rjust(25))
    print('-' * (maxlen + 35))
    for app in sorted(appdata):
        print(app.ljust(maxlen) + str(appdata[app]['methods']).rjust(10)
                  + str(appdata[app]['analysistime']).rjust(25))
    print('-' * (maxlen + 35))
    exit(0)

def show_bytecode(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    cmsix: int = args.cmsix
    save: bool = args.save
    showstack: bool = args.showstack
    showtargets: bool = args.showtargets
    showinvariants: bool = args.showinvariants

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    lines = []
    if showstack or showtargets or showinvariants:
        bytecodereport = BRP.BytecodeReport(app, cmsix)
        lines.append(bytecodereport.to_string(showstack= showstack,
                                                  showtargets= showtargets,
                                                  showinvariants= showinvariants))
    else:
        lines.append(str(app.get_method(cmsix)))

    if save:
        UCC.save(path, 'byte_code_' + str(cmsix) + '.txt',lines)   
    else:
        print('\n'.join(lines))
    exit(0)

def show_apis(args: argparse.Namespace) -> NoReturn:
    engagments: str = args.engagements
    verbose:bool = args.verbose

    engagements = [ 'E2', 'E4', 'E5', 'E6', 'E7' ]

    target = engagments
    if target == 'all':
        etargets = engagements
    else:
        etargets = [ target ]

    engagementdata = UF.get_engagements_data_file()
    engagementsdir = UF.get_engagements_directory()

    app_apis: Dict[str, List[str]] = {}  # app -> api list

    for e in etargets:

        edata = engagementdata[e]
        edir = os.path.join(engagementsdir,e)

        for app in sorted(edata['apps']):
            appdata = edata['apps'][app]
            appdir = os.path.join(edir,app)
            apisused = os.path.join(appdir,'APIsUsed.txt')
            with open(apisused,'r') as fp:
                app_apis[app] = fp.readlines()

    apis: Dict[str, List[str]] = {}  # api -> app list

    for app in sorted(app_apis):
        for l in app_apis[app]:
            l = l.strip()
            apis.setdefault(l,[])
            apis[l].append(app)

    if verbose:
        for api in sorted(apis):
            print('\n' + api)
            for app in sorted(apis[api]):
                print('  ' + app)

        print('\nNumber of apis: ' + str(len(apis)))

    else:
        for api in sorted(apis):
            print(str(len(apis[api])).rjust(4) + '  ' + api)
        print('\nNumber of apis: ' + str(len(apis)))
    exit(0)

def show_dependencies(args: argparse.Namespace) -> NoReturn:
    engagements: List[str] = args.engagement
    verbose: bool = args.verbose

    allengagements = [ 'E2', 'E4', 'E5', 'E6', 'E7' ]

    dependencies: Dict[str, List[str]] = {}

    if 'all' in engagements:
        engagements = allengagements

    engagementfile = UF.get_engagements_data_file()

    for engagement in engagements:
        appdata = engagementfile[engagement]['apps']

        for app in sorted(appdata):
            if 'dependencies' in appdata[app]:
                for d in appdata[app]['dependencies']:
                    dependencies.setdefault(d,[])
                    dependencies[d].append(app)
            else:
                print('Missing dependencies for ' + app)

    if verbose:
        for d in sorted(dependencies):
            print('\n' + d)
            for app in sorted(dependencies[d]):
                print('  ' + app)

    else:
        for d in sorted(dependencies):
            print(str(len(dependencies[d])).rjust(4) + '  ' + d) 
    exit(0)

def show_questions(args: argparse.Namespace) -> NoReturn:
    engagement: str = args.engagement
    time: bool = args.time
    space: bool = args.space
    complexity: bool = args.complexity
    sidechannel: bool = args.sidechannel

    questions: Dict[str, Tuple[Dict[str, Dict[str, str]], str]] = {}

    def selected(qtype: str, qresource: str) -> bool:
        def resource_selected() -> bool:
            return ((qresource == 'time' and not space)
                        or (qresource == 'space' and not time)
                        or (qresource == 'space/time'))
        if (time or space or complexity or sidechannel):
            if qtype == 'complexity' and not sidechannel:
                return resource_selected()
            if qtype == 'side channel' and not complexity:
                return resource_selected()
            return False
        return True

    datafile = UF.get_engagements_data_file()
    appdata = datafile[args.engagement]['apps']

    header = 'Questions '
    if complexity: header += ' (complexity)'
    if sidechannel: header += ' (side channel)'
    if time: header += ' (time)'
    if time: header += ' (space)'

    for app in sorted(appdata):
        for q in appdata[app]['questions']:
            if q in questions:
                print('duplicated for ' + q)
                exit(1)
            questions[q] = (appdata[app]['questions'][q],app)

    lines = []

    for n in sorted(questions):
        (q,app) = questions[n]
        secret = ''
        if q['type'] == 'side channel':
            secret = q['secret'] + ', ' + str(q['operations']) + ' ops (' + q['resource'] + ')'
        resources = ''
        if q['type'] == 'complexity':
            resources = ('(' + str(q['resource']) + ', ' + str(q['inputbudget']) + ', ' +
                             str(q['usagelimit']) + ')')

        if selected(q['type'],q['resource']):
            lines.append(n + '  ' + app.ljust(30) + q['type'].ljust(10) + '  ' + secret + resources)

    print(header + ': ' + str(len(lines)))
    print('\n'.join(lines))
    exit(0)


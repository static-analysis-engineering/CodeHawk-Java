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
"""Prints out the dependencies for one or all engagements"""

import argparse
import os

import chj.util.fileutil as UF

engagements = [ 'E2', 'E4', 'E5', 'E6', 'E7' ]

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engagement',help='engagement to prepare',
                            choices=(engagements + ['all']))
    parser.add_argument('--verbose',action='store_true',
                            help='print out applications that use api')
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse()

    target = args.engagement
    if target == 'all':
        etargets = engagements
    else:
        etargets = [ target ]

    engagementdata = UF.get_engagements_data_file()
    engagementsdir = UF.get_engagements_directory()

    app_apis = {}  # app -> api list

    for e in etargets:

        edata = engagementdata[e]
        edir = os.path.join(engagementsdir,e)

        for app in sorted(edata['apps']):
            appdata = edata['apps'][app]
            appdir = os.path.join(edir,app)
            apisused = os.path.join(appdir,'APIsUsed.txt')
            with open(apisused,'r') as fp:
                app_apis[app] = fp.readlines()

    apis = {}  # api -> app list

    for app in sorted(app_apis):
        for l in app_apis[app]:
            l = l.strip()
            apis.setdefault(l,[])
            apis[l].append(app)

    if args.verbose:
        for api in sorted(apis):
            print('\n' + api)
            for app in sorted(apis[api]):
                print('  ' + app)

        print('\nNumber of apis: ' + str(len(apis)))
        
    else:
        for api in sorted(apis):
            print(str(len(apis[api])).rjust(4) + '  ' + api)
        print('\nNumber of apis: ' + str(len(apis)))
    
        

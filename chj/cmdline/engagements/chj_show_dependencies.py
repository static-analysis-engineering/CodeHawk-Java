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

import chj.util.fileutil as UF

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engagements',nargs='*',
                            choices=['all','E2','E4','E5','E6','E7'],
                            help='name of engagement (E2, E4, E5, E6, or E7)')
    parser.add_argument('--verbose',action='store_true',
                            help='print applications that use dependency')
    args = parser.parse_args()
    return args

questions = {}

if __name__ == '__main__':

    args = parse()
    dependencies = {}

    allengagements = [ 'E2', 'E4', 'E5', 'E6', 'E7' ]

    if 'all' in args.engagements:
        engagements =  allengagements
    else:
        engagements = args.engagements

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

    if args.verbose:
        for d in sorted(dependencies):
            print('\n' + d)
            for app in sorted(dependencies[d]):
                print('  ' + app)

    else:
        for d in sorted(dependencies):
            print(str(len(dependencies[d])).rjust(4) + '  ' + d)

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

import chj.util.fileutil as UF

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('engagement',help='name of engagement (E2, E4, E5, E6, or E7)',
                            choices=['E2','E4','E5','E6','E7'])
    parser.add_argument('--time',help='only show questions with time resource',
                            action='store_true')
    parser.add_argument('--space',help='only show questions with space resource',
                            action='store_true')
    parser.add_argument('--complexity', help='only show complexity questions',
                            action='store_true')
    parser.add_argument('--sidechannel',help='only show side-channel questions',
                            action='store_true')
    args = parser.parse_args()
    return args

questions = {}

if __name__ == '__main__':

    args = parse()

    def selected(qtype,qresource):
        def resource_selected():
            return ((qresource == 'time' and not args.space)
                        or (qresource == 'space' and not args.time)
                        or (qresource == 'space/time'))
        if (args.time or args.space or args.complexity or args.sidechannel):
            if qtype == 'complexity' and not args.sidechannel:
                return resource_selected()
            if qtype == 'side channel' and not args.complexity:
                return resource_selected()
            return False
        return True

    datafile = UF.get_engagements_data_file()
    appdata = datafile[args.engagement]['apps']

    header = 'Questions '
    if args.complexity: header += ' (complexity)'
    if args.sidechannel: header += ' (side channel)'
    if args.time: header += ' (time)'
    if args.time: header += ' (space)'

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

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
    args = parser.parse_args()
    return args

questions = {}

if __name__ == '__main__':

    args = parse()

    appdata = UF.get_engagements_data_file()[args.engagement]['apps']

    maxlen = max([ len(app) for app in appdata ] ) + 2

    print('application'.ljust(maxlen) + 'methods'.rjust(10) + 'analysis time (secs)'.rjust(25))
    print('-' * (maxlen + 35))
    for app in sorted(appdata):
        print(app.ljust(maxlen) + str(appdata[app]['methods']).rjust(10)
                  + str(appdata[app]['analysistime']).rjust(25))
    print('-' * (maxlen + 35))

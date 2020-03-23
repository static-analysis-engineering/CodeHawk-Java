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
"""Populates the STAC Engagements repository with jars and associated information"""

import argparse
import os
import shutil

import chj.util.fileutil as UF

engagements = [ 'E2', 'E4', 'E5', 'E6', 'E7' ]

def parse():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('srcdir',help='directory to copy engagement data from')
    parser.add_argument('tgtdir',help='directory to copy engagement data to')
    parser.add_argument('engagement',help='engagement to prepare',
                            choices=(engagements + ['all']))
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse()

    if not os.path.isdir(args.srcdir):
        print('Source directory: ' + args.srcdir + ' not found')
        exit(0)

    if not os.path.isdir(args.tgtdir):
        print('Target directory: ' + args.tgtdir + ' not found')
        exit(0)

    target = args.engagement
    if target == 'all':
        etargets = engagements
    else:
        etargets = [ target ]
    
    engagementdata = UF.get_engagements_data_file()

    for e in etargets:

        esrcpath = os.path.join(args.srcdir,e)
        if not os.path.isdir(esrcpath):
            print('Source engagement directory: ' + esrcpath + ' not found')
            exit(0)

        # create target directory, if necessary
        etgtpath = os.path.join(args.tgtdir,e)
        if not os.path.isdir(etgtpath):
            os.mkdir(etgtpath)

        edata = engagementdata[e]

        for app in sorted(edata['apps']):

            print('Copying data for ' + app)

            appdata = edata['apps'][app]
            
            appsrcpath = os.path.join(esrcpath,app)
            if not os.path.isdir(appsrcpath):
                print('Source application  directory: '  + appsrcpath + ' not found')
                exit(0)

            # create application directory, if necessary
            apptgtpath = os.path.join(etgtpath,app)
            if not os.path.isdir(apptgtpath):
                os.mkdir(apptgtpath)
            tgtquestions = os.path.join(apptgtpath,'questions')
            tgtchallenge = os.path.join(apptgtpath,'challenge_program')
            if  not os.path.isdir(tgtquestions):
                os.mkdir(tgtquestions)
            if not os.path.isdir(tgtchallenge):
                os.mkdir(tgtchallenge)

            # copy APIsUsed, description, and questions
            apisused = os.path.join(appsrcpath,'APIsUsed.txt')
            description = os.path.join(appsrcpath,'description.txt')
            questions = os.path.join(appsrcpath,'questions')
            challenge = os.path.join(appsrcpath,'challenge_program')

            if os.path.isfile(apisused):
                shutil.copy(apisused,apptgtpath)

            if os.path.isfile(description):
                shutil.copy(description,apptgtpath)

            if os.path.isdir(questions):
                for f in os.listdir(questions):
                    f = os.path.join(questions,f)
                    shutil.copy(f,tgtquestions)

            if os.path.isdir(challenge):
                
                for jar in appdata['jars']:
                    jardir = os.path.dirname(jar)
                    if not jardir == '':
                        tgtjardir = os.path.join(tgtchallenge,jardir)
                        if not os.path.isdir(tgtjardir):
                            os.makedirs(tgtjardir)
                    else:
                        tgtjardir = tgtchallenge
                    srcjar = os.path.join(challenge,jar)                        
                    shutil.copy(srcjar,tgtjardir)

            

    

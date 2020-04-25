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
import os
import subprocess

import chj.cmdline.AnalysisManager as AM
import chj.util.fileutil as UF
import chj.util.xmlutil as UX

from chj.index.AppAccess import AppAccess

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('appname',help='name of engagement application')
    parser.add_argument('cmsix',help='index of the method to be annotated',type=int)
    parser.add_argument('targetclass',help='name of target class name for virtual call')
    parser.add_argument('--pcs',nargs='*',type=int,help='list of instruction offsets')
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = parse()

    try:
        (path,jars) = UF.get_engagement_app_jars(args.appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        exit(1)

    app = AppAccess(path)

    cms = app.jd.get_cms(args.cmsix)
    cnix = cms.cnix
    msix = cms.msix
    (methodname,methodsig) = app.jd.mssignatures[msix]

    if not app.has_user_data_class(cnix):
        cn = app.jd.get_cn(cnix)
        package = cn.get_package_name()
        cname = cn.get_simple_name()
        newuserclass = UX.create_user_class_xnode(package,cname)
        UF.save_userdataclass_file(path,package,cname,newuserclass)

    userclass = app.get_user_data_class(cnix)
    if not userclass.has_method(msix):
        userclass.mk_method(methodname,methodsig,msix)
        
    usermethod = userclass.get_method(msix)
    for pc in args.pcs:
        usermethod.add_callee_restriction(pc,args.targetclass)

    userclass.save_xml()
    
    print(str(usermethod))

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

import argparse, sys

import chj.util.fileutil as UF
import chj.util.xmlutil as UX
import chj.cmdline.AnalysisManager as AM
import chj.cmdline.commandutils as UCC

from chj.index.AppAccess import AppAccess

from contextlib import contextmanager

from typing import List, Optional, NoReturn

def init_user_data_class(path: str, app: AppAccess, cnix: int) -> None:
    if not app.has_user_data_class(cnix):
        cn = app.jd.get_cn(cnix)
        package = cn.get_package_name()
        cname = cn.get_simple_name()
        newuserclass = UX.create_user_class_xnode(package, cname)
        UF.save_userdataclass_file(path, package, cname, newuserclass)

def callee_restriction(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    cmsix: int = args.cmsix
    targetclass: str = args.targetclass
    pcs: Optional[List[int]] = args.pcs

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    cms = app.jd.get_cms(cmsix)
    cnix = cms.cnix
    msix = cms.msix
    (methodname,methodsig) = app.jd.mssignatures[msix]

    init_user_data_class(path, app, cnix)

    userclass = app.get_user_data_class(cnix)
    if not userclass.has_method(msix):
        userclass.mk_method(methodname,methodsig,msix)

    usermethod = userclass.get_method(msix)
    if pcs is not None:
        for pc in pcs:
            usermethod.add_callee_restriction(pc, targetclass)

    userclass.save_xml()
   
    print(str(usermethod))
    exit(0)

def interface_target(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    cmsix: int = args.cmsix
    interface: str = args.interface
    targetclass: str = args.targetclass

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    cms = app.jd.get_cms(cmsix)
    cnix = cms.cnix
    msix = cms.msix
    (methodname,methodsig) = app.jd.mssignatures[msix]

    init_user_data_class(path, app, cnix)

    userclass = app.get_user_data_class(cnix)
    if not userclass.has_method(msix):
        userclass.mk_method(methodname,methodsig,msix)

    usermethod = userclass.get_method(msix)
    usermethod.add_interface_restriction(interface, targetclass)

    userclass.save_xml()
   
    print(str(usermethod))
    exit(0)

def loopbound(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    cmsix: int = args.cmsix
    pc: int = args.pc
    constant: Optional[int] = args.constant
    symbolic: Optional[str] = args.symbolic

    if constant is None and symbolic is None:
        print('*' * 80)
        print('Please specify either a constant or a symbolic value')
        print('*' * 80)
        exit(1)

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    cms = app.jd.get_cms(cmsix)
    cnix = cms.cnix
    msix = cms.msix
    (methodname, methodsig) = app.jd.mssignatures[msix]

    init_user_data_class(path, app, cnix)

    userclass = app.get_user_data_class(cnix)
    if not userclass.has_method(msix):
        userclass.mk_method(methodname,methodsig,msix)

    usermethod = userclass.get_method(msix)
    if not constant is None:
        usermethod.add_numeric_bound(pc, constant)
    elif not symbolic is None:
        usermethod.add_symbolic_bound(pc, symbolic)

    userclass.save_xml()
   
    print(str(usermethod))
    exit(0)    

def methodcost(args: argparse.Namespace) -> NoReturn:
    appname: str = args.appname
    cmsix: int = args.cmsix
    cost: int = args.cost
    lb: int = args.lb
    ub: int = args.ub

    path = UCC.check_app_analysisdir(appname)
    app = AppAccess(path)

    mcost = []
    if not cost is None:
        mcost.append(('icost', cost))
    else:
        if not lb is None:
            mcost.append(('lb', lb))
        if not ub is None:
            mcost.append(('ub', ub))

    if len(mcost) == 0:
        print('*' * 80)
        print('Please specify either a constant or at least one bound')
        print('*' * 80)
        exit(1)

    cms = app.jd.get_cms(cmsix)
    cnix = cms.cnix
    msix = cms.msix
    (methodname, methodsig) = app.jd.mssignatures[msix]

    init_user_data_class(path, app, cnix)

    userclass = app.get_user_data_class(cnix)
    if not userclass.has_method(msix):
        userclass.mk_method(methodname,methodsig,msix)

    usermethod = userclass.get_method(msix)
    usermethod.add_method_cost(mcost)

    userclass.save_xml()
   
    print(str(usermethod))
    exit(0)

# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2020 Kestrel Technology LLC
# Copyright (c) 2021      Andrew McGraw
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

import os
import zipfile
import xml.etree.ElementTree as ET

from chj.util.Config import Config
import chj.util.fileutil as UF

from chj.libsum.ClassSummary import ClassSummary

from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.AppAccess import AppAccess

class JDKModels():

    def __init__(self, app: "AppAccess"):
        self.app = app
        self.jdkjar = zipfile.ZipFile(Config().jdksummaries,'r')
        self.filenames = []
        for info in self.jdkjar.infolist():
            if info.filename.endswith('.xml') and not (info.filename == 'jdk_jar_version.xml'):
                self.filenames.append(info.filename)

    def get_class_count(self) -> int: 
        return len(self.filenames)

    def iter_class_summaries(self, f:Callable[[str, ClassSummary], None]) -> None:
        for cn in self.filenames:
            classfile_summary = self.get_classfile_summary(cn)
            if classfile_summary is not None:
                f(cn,classfile_summary)

    def iter_package_class_summaries(self, package: str, f:Callable[[str, ClassSummary], None]) -> None:
        for cn in self.filenames:
            summary = self.get_class_summary(cn)
            if summary is not None and summary.package == package:
                f(cn,summary)

    def has_class_summary(self, classname: str) -> bool:
        filename = classname.replace('.','/') + '.xml'
        return filename in self.filenames

    def get_class_summary(self, classname: str) -> Optional[ClassSummary]:
        if self.has_class_summary(classname):
            classfilename = classname.replace('.','/') + '.xml'
            xnode = self._get_class_summary_xnode(classfilename)
            if not xnode is None:
                return ClassSummary(self,xnode)
            print('Unable to read summary for ' + classname)
        print('No summary found for ' + classname)
        return None

    def get_classfile_summary(self, classfilename: str) -> Optional[ClassSummary]:
        xnode = self._get_class_summary_xnode(classfilename)
        if not xnode is None:
            return ClassSummary(self,xnode)
        print('Unable to read summary for ' + classfilename)
        return None

    def _get_class_summary_xnode(self, classfilename: str) -> Optional[ET.Element]:
        errormsg = ' missing from xml for ' + classfilename
        try:
            zfile = self.jdkjar.read(classfilename)
            xnode = UF.safe_find(ET.fromstring(str(zfile)), 'header', 'header ' + errormsg)
            if 'info' in xnode.attrib:
                info = UF.safe_get(xnode, 'info', 'info ' + errormsg, str)
                xnode = UF.safe_find(ET.fromstring(str(zfile)), info, 'info ' + errormsg)
            else:
                xnode = UF.safe_find(ET.fromstring(str(zfile)), 'class', 'class ' + errormsg)
                if xnode is None:
                    xnode = UF.safe_find(ET.fromstring(str(zfile)), 'interface', 'interface ' + errormsg)
            if xnode is None:
                print('Unable to load ' + classfilename)
            return xnode
        except Exception as e:
            print('Error in reading ' + classfilename + ':' + str(e))
            return None 

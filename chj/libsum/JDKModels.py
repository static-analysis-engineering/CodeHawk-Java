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

import os
import zipfile
import xml.etree.ElementTree as ET

from chj.util.Config import Config

from chj.libsum.ClassSummary import ClassSummary

class JDKModels():

    def __init__(self,app):
        self.app = app
        self.jdkjar = zipfile.ZipFile(Config().jdksummaries,'r')
        self.filenames = []
        for info in self.jdkjar.infolist():
            if info.filename.endswith('.xml') and not (info.filename == 'jdk_jar_version.xml'):
                self.filenames.append(info.filename)

    def get_class_count(self): return len(self.filenames)

    def iter_class_summaries(self,f):
        for cn in self.filenames: f(cn,self.get_classfile_summary(cn))

    def iter_package_class_summaries(self,package,f):
        for cn in self.filenames:
            summary = self.get_class_summary(cn)
            if summary.package == package: f(cn,summary)

    def has_class_summary(self,classname):
        filename = classname.replace('.','/') + '.xml'
        return filename in self.filenames

    def get_class_summary(self,classname):
        if self.has_class_summary(classname):
            classfilename = classname.replace('.','/') + '.xml'
            xnode = self._get_class_summary_xnode(classfilename)
            if not xnode is None:
                return ClassSummary(self,xnode)
            print('Unable to read summary for ' + classname)
        print('No summary found for ' + classname)

    def get_classfile_summary(self,classfilename):
        xnode = self._get_class_summary_xnode(classfilename)
        if not xnode is None:
            return ClassSummary(self,xnode)
        print('Unable to read summary for ' + classfilename)

    def _get_class_summary_xnode(self,classfilename):
        try:
            zfile = self.jdkjar.read(classfilename)
            xnode = ET.fromstring(str(zfile)).find('header')
            if 'info' in xnode.attrib:
                info = xnode.get('info')
                xnode = ET.fromstring(str(zfile)).find(info)
            else:
                xnode = ET.fromstring(str(zfile)).find('class')
                if xnode is None:
                    xnode = ET.fromstring(str(zfile)).find('interface')
            if xnode is None:
                print('Unable to load ' + classfilename)
            return xnode
        except Exception as e:
            print('Error in reading ' + classfilename + ':' + str(e))
        

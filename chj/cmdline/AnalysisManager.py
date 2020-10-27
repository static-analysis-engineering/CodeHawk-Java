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
import shutil
import subprocess

import chj.util.fileutil as UF

from chj.util.Config import Config

class AnalysisManager():

    def __init__(self,path,jars,platform=None,excludes=[],dependencies=[],verbose=False,dbg=False):
        """Initialize analyzer location and target jar locations

        Arguments:
        path    -- path of the directory in which to save the analysis results
        jars    -- list of jar file names to be included in the analysis
                   (relative to path, or absolute)
        platform  -- platform name to locate platform-specific summaries
        excludes -- list of package prefixes; classnames that start with one of 
                    these are not loaded
        dependencies -- list of library jars used by the application
        """

        self.config = Config()
        self.platform = platform
        # self.jdksummaries = UF.get_jdksummaries_filename(platform)
        self.jdksummaries = self.config.jdksummaries
        self.apppath = path
        self.verbose = verbose
        self.dbg = dbg
        if self.apppath[-1] == '/': self.apppath = self.apppath[:-1]
        self.jars = jars
        self.excludes = excludes
        self.dependencies = dependencies
        self.missinglibraries =  []

    def _makedir(self,name):
        if os.path.isdir(name): return
        os.mkdir(name)

    def get_dependency_summary_jar(self,dep):
        try:
            return UF.get_lib_summary_jarfile_name(dep,self.platform)
        except UF.CHJLibraryJarNotFoundError as e:
            print('Dependency jar ' + e.libjar + ' not found')
            self.missinglibraries.append(dep)
            return None
        except UF.CHJError as e:
            print(str(e.wrap()))
            exit(1)

    def add_dependencies(self,cmd):
        for d in self.dependencies:
            dfile = self.get_dependency_summary_jar(d)
            if dfile is None: continue
            cmd.extend(['-summaries',dfile])

    def add_excludes(self,cmd):
        for s in self.excludes:
            cmd.extend(['-exclude_pkg_prefix',s])

    def add_jars(self,cmd):
        cmd.append('-jars')
        for jar in self.jars:
            cmd.append(jar)

    def analyze(self,intervalsonly=False):
        os.chdir(self.apppath)
        cmd = [ self.config.analyzer, '-summaries', self.jdksummaries ]
        self.add_dependencies(cmd)
        self.add_excludes(cmd)
        if self.verbose: cmd.append('-verbose')
        self.add_jars(cmd)
        print('Executing: ' + ' '.join(cmd))
        try:
            result = subprocess.call(cmd, cwd=self.apppath,stderr=subprocess.STDOUT)
        except OSError as e:
            raise UF.CHJOSErrorInAnalyzer(cmd,e)
        except subprocess.CalledProcessError as e:
            raise UF.CHJProcessErrorInAnalyzer(cmd,e)
        if result == 0:
            return
        else:
            raise UF.CHJCodeHawkAnalyzerError(cmd,result)

    def translate_only(self):
        os.chdir(self.apppath)
        cmd = [ self.config.analyzer, '-summaries', self.jdksummaries,
                    '-translate_only' ]
        self.add_dependencies(cmd)
        self.add_excludes(cmd)
        self.add_jars(cmd)
        print('Executing: ' + ' '.join(cmd))
        try:
            result = subprocess.call(cmd, cwd=self.apppath, stderr=subprocess.STDOUT)
        except OSError as e:
            raise UF.CHJOSErrorInAnalyzer(cmd,e)
        except subprocess.CalledProcessError as e:
            raise UF.CHJProcessErrorInAnalyzer(cmd,e)
        if result == 0:
            return
        else:
            raise UF.CHJCodeHawkAnalyzerError(cmd,result)

    def rungui(self):
        os.chdir(self.apppath)
        cmd = [ self.config.gui, '-summaries', self.jdksummaries ]
        self.add_dependencies(cmd)
        self.add_excludes(cmd)
        self.add_jars(cmd)
        print('Running the gui: ' + ' '.join(cmd))
        try:
            result = subprocess.call(cmd, cwd = self.apppath, stderr=subprocess.STDOUT)
        except OSError as e:
            raise UF.CHJOSErrorInAnalyzer(cmd,e)
        except subprocess.CalledProcessError as e:
            raise UF.CHJProcessErrorInAnalyzer(cmd,e)
        if result == 0:
            return
        else:
            raise UF.CHJCodeHawkAnalyzerError(cmd,result)

    def scanonly(self,verbose=False):
        os.chdir(self.apppath)
        print('cd ' + self.apppath)
        cmd = [ self.config.analyzer, '-summaries', self.jdksummaries,'-scan_only']
        if verbose:
            cmd.append('-verbose')
        self.add_dependencies(cmd)
        self.add_excludes(cmd)
        self.add_jars(cmd)
        print('Executing: ' + ' '.join(cmd))
        try:
            result = subprocess.call(cmd, cwd=self.apppath, stderr=subprocess.STDOUT)
        except OSError as e:
            raise UF.CHJOSErrorInAnalyzer(cmd,e)
        except subprocess.CalledProcessError as e:
            raise UF.CHJProcessErrorInAnalyzer(cmd,e)
        if result == 0:
            return
        else:
            raise UF.CHJCodeHawkAnalyzerError(cmd,result)

    def create_cost_model(self,silent=False,space=False):
        os.chdir(self.apppath)
        cmd = [ self.config.analyzer, '-summaries', self.jdksummaries,
                    '-costmodel' ]
        self.add_dependencies(cmd)
        self.add_excludes(cmd)
        if self.verbose: cmd.append('-verbose')
        if self.dbg: cmd.append('-dbg')
        self.add_jars(cmd)            
        print('Executing: ' + ' '.join(cmd))
        try:
            result = subprocess.call(cmd,cwd=self.apppath,stderr=subprocess.STDOUT)
        except OSError as e:
            raise UF.CHJOSErrorInAnalyzer(cmd,e)
        except subprocess.CalledProcessError as e:
            raise UF.CHJProcessErrorInAnalyzer(cmd,e)
        if result == 0:
            return
        else:
            raise UF.CHJCodeHawkAnalyzerError(cmd,result)

    def create_taint_graphs(self,silent=False,space=False):
        os.chdir(self.apppath)
        cmd = [ self.config.analyzer, '-summaries', self.jdksummaries,
                    '-taint' ]
        self.add_dependencies(cmd)
        self.add_excludes(cmd)
        if self.verbose: cmd.append('-verbose')
        if self.dbg: cmd.append('-dbg')
        self.add_jars(cmd)            
        print('Executing: ' + ' '.join(cmd))
        try:
            result = subprocess.call(cmd,cwd=self.apppath,stderr=subprocess.STDOUT)
        except OSError as e:
            raise UF.CHJOSErrorInAnalyzer(cmd,e)
        except subprocess.CalledProcessError as e:
            raise UF.CHJProcessErrorInAnalyzer(cmd,e)
        if result == 0:
            return
        else:
            raise UF.CHJCodeHawkAnalyzerError(cmd,result)

    def create_taint_trail(self,taintindex,silent=False,space=False):
        os.chdir(self.apppath)
        cmd = [ self.config.analyzer, '-summaries', self.jdksummaries,
                    '-taintorigin', str(taintindex) ]
        self.add_dependencies(cmd)
        self.add_excludes(cmd)
        if self.verbose: cmd.append('-verbose')
        if self.dbg: cmd.append('-dbg')
        self.add_jars(cmd)
        print('Executing: ' + ' '.join(cmd))
        try:
            stdout = subprocess.DEVNULL if silent else subprocess.STDOUT
            result = subprocess.call(cmd,cwd=self.apppath,stdout=stdout,stderr=subprocess.STDOUT)
        except OSError as e:
            raise UF.CHJOSErrorInAnalyzer(cmd,e)
        except subprocess.CalledProcessError as e:
            raise UF.CHJProcessErrorInAnalyzer(cmd,e)
        if result == 0:
            return
        else:
            raise UF.CHJCodeHawkAnalyzerError(cmd,result)

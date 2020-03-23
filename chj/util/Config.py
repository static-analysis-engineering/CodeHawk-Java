# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Henny Sipma
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016-2019 Kestrel Technology LLC
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

if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ConfigLocal.py")):
    import chj.util.ConfigLocal as ConfigLocal

class Config():

    def __init__(self):
        """Locations of executables and summaries.

        bindir: location of the codehawk executables:
        the following executables are expected:
        - chj_initialize

        default location is the bin directory, but another (absolute) path
        can be specified by the user in ConfigLocal.py

        summariesdir: location of jkdsummaries.jar
           jdksummaries.jar contains summaries of of the JDK library classes
           (currently more than 10,000 methods)

        default location is jdksum directory, but another (absolute) path
        can be specified by the user in ConfigLocal.py
        """
        # platform settings
        if os.uname()[0] == 'Linux': self.platform = 'linux'
        elif os.uname()[0] == 'Darwin': self.platform = 'macOS'

        # default settings
        self.utildir = os.path.dirname(os.path.abspath(__file__))
        self.chjdir = os.path.dirname(self.utildir)
        self.bindir = os.path.join(self.chjdir,'binaries')
        self.rootdir = os.path.dirname(self.chjdir)
        self.summariesdir = os.path.join(self.chjdir,'summaries')
        self.jdksummaries = os.path.join(self.summariesdir,'jdk.jar')
        self.libsumindex = None
        self.platforms = {}

        # analyzer and gui executables
        if self.platform == 'linux':
            self.linuxdir = os.path.join(self.bindir,'linux')
            self.analyzer = os.path.join(self.linuxdir,'chj_initialize')
            self.gui = os.path.join(self.linuxdir,'chj_gui')

        elif self.platform == 'macOS':
            self.macOSdir = os.path.join(self.bindir,'macOS')
            self.analyzer = os.path.join(self.macOSdir,'chj_initialize')
            self.gui = os.path.join(self.macOSdir,'chj_gui')

        else:
            self.analyzer = None
            self.gui = None

        # STAC Engagements
        self.stacrepodir = None

        if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ConfigLocal.py")):
            ConfigLocal.getLocals(self)

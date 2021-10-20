# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Andrew McGraw
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
import subprocess

import chj.util.fileutil as UF
import chj.cmdline.AnalysisManager as AM
import chj.index.AppAccess as AP

from typing import Optional

def analyze_taint_propagation(appname: str, origin: int) -> Optional[AP.AppAccess]:
    try:
        UF.check_analyzer()
        (path,jars) = UF.get_engagement_app_jars(appname)
        UF.check_analysisdir(path)
    except UF.CHJError as e:
        print(str(e.wrap()))
        return None

    pkg_excludes = UF.get_engagement_app_excludes(appname)
    dependencies = UF.get_engagement_app_dependencies(appname)

    am = AM.AnalysisManager(path,jars,dependencies=dependencies,excludes=pkg_excludes)

    try:
        am.create_taint_trail(origin, silent=True)
        app = reload_engagement_app(appname)
        return app
    except UF.CHJError as e:
        print(str(e.wrap()))
        return None

#Useful when the analysis has changed the xml results
def reload_engagement_app(project: str) -> AP.AppAccess:
    (path, jars) = UF.get_engagement_app_data(project)
    UF.check_analysisdir(path)
    app = AP.AppAccess(path)
    return app

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
"""Utility functions to load and save bytecode and analysis results."""

import datetime
import json
import os
import shutil

import xml.etree.ElementTree as ET
import chj.util.xmlutil as UX

from typing import Any, cast, Dict, List, Optional, Tuple, Type, TypeVar

from chj.util.Config import Config
config = Config()

class CHError(Exception):

    def wrap(self) -> str:
        lines = []
        lines.append('*' * 80)
        lines.append(self.__str__())
        lines.append('*' * 80)
        return '\n'.join(lines)

class CHJError(CHError):

    def __init__(self, msg: str) -> None:
        CHError.__init__(self,msg)

class CHJFileNotFoundError(CHJError):

    def __init__(self, filename: str) -> None:
        CHJError.__init__(self,'File ' + filename + ' not found')
        self.filename = filename

class CHJDirectoryNotFoundError(CHJError):

    def __init__(self, dirname: str) -> None:
        CHJError.__init__(self,'Directory ' + dirname + ' not found')
        self.dirname = dirname

class CHJAnalyzerNotSetError(CHJError):

    def __init__(self) -> None:
        CHJError.__init__(self,'Location of CodeHawk Java Analyzer has not been set')

    def __str__(self) -> str:
        return ('The location of the CodeHawk Java Analyzer has not been set in '
                    + 'the configuration file. Maybe the platform is not recognized.')

class CHJAnalyzerNotFoundError(CHJFileNotFoundError):

    def __init__(self, filename: str) -> None:
        CHJFileNotFoundError.__init__(self,filename)

    def __str__(self) -> str:
        return ('No analyzer executable found at ' + self.filename)

class CHJGuiNotSetError(CHJError):

    def __init__(self) -> None:
        CHJError.__init__(self,'Location of CodeHawk Java Analyzer Gui has not been set')

    def __str__(self) -> str:
        return ('The location of the CodeHawk Java Analyzer Gui has not been set in '
                    + 'the configuration file. Maybe the platform is not recognized.')

class CHJGuiNotFoundError(CHJFileNotFoundError):

    def __init__(self,filename: str) -> None:
        CHJFileNotFoundError.__init__(self,filename)

    def __str__(self) -> str:
        return ('No gui executable found at ' + self.filename)

class CHJJDKSummariesLocationNotSetError(CHJError):

    def __init__(self,platform: Optional[str]) -> None:
        CHJError.__init__(self,'JDK summaries file location not set')
        self.platform = platform

    def __str__(self) -> str:
        if self.platform is None:
            return ('Location of jdk summaries file not set in Config file')
        else:
            return('Location of jdk summaries file not set for platform '
                       + self.platform + ' in platform data record')

class CHJJDKSummariesFileNotFoundError(CHJFileNotFoundError):

    def __init__(self, platform: Optional[str], filename: str) -> None:
        CHJFileNotFoundError.__init__(self,filename)
        self.platform = platform

    def __str__(self) -> str:
        if self.platform is None:
            return ('Jdk summaries file: ' + self.filename + ' not found')
        else:
            return('Jdk summaries file: ' + self.filename + ' for platform '
                       + self.platform + ' not found')

class CHJLibSumIndexLocationNotSetError(CHJError):
    def __init__(self, platform: Optional[str]) -> None:
        CHJError.__init__(self, 'JDK summaries file location not set')
        self.platform = platform

    def __str__(self) -> str:
        if self.platform is None:
            return ('Location of library summaries index file not set in config file')
        else:
            return('Location of library summaries file not set for platform '
                        + self.platform + ' in platform data record')

class CHJLibSumIndexLocationNotFoundError(CHJError):

    def __init__(self, platform: str) -> None:
        CHJError.__init__(self,'Index file for library summaries not found')
        self.platform = platform

    def __str__(self) -> str:
        if self.platform is None:
            return ('Index file for library summaries not set in Config file')
        else:
            return ('Index file for library summaries for platform '
                        + self.platform + ' not set in platform data record')

class CHJLibraryJarNotFoundError(CHJError):

    def __init__(self, libjar: str) -> None:
        CHJError.__init__(self,'Library jar not found in index')
        self.libjar = libjar

    def __str__(self) -> str:
        return ('Library jar ' + self.libjar + ' not listed in library summary index')


class CHJLibrarySummaryJarNotFoundError(CHJFileNotFoundError):

    def __init__(self, filename: str) -> None:
        CHJFileNotFoundError.__init__(self,filename)

    def __str__(self) -> str:
        return ('Library summary jar ' + self.filename + ' not found')

class CHJLibSumIndexFileNotFoundError(CHJFileNotFoundError):

    def __init__(self,platform: str, filename: str) -> None:
        CHJFileNotFoundError.__init__(self,filename)
        self.platform = platform

    def __str__(self) -> str:
        return ('Index file for library summaries not found at ' +  self.filename)

class CHJAnalysisResultsNotFoundError(CHJError):

    def __init__(self, path: str) -> None:
        CHJError.__init__(self,'No analysis results found for: ' + path
                              + '\nPlease analyze project first.')
        self.path = path

class CHJJSONParseError(CHJError):

    def __init__(self, filename: str, e: ValueError) -> None:
        CHJError.__init__(self,'JSON parse error')
        self.filename = filename
        self.valueerror = e

    def __str__(self) -> str:
        return ('JSON parse error in file: ' + self.filename + ': '
                    + str(self.valueerror))

class CHJXmlParseError(CHJError):

    def __init__(self, 
            filename: str, 
            errorcode: int, 
            position: Tuple[int, int]) -> None:
        CHJError.__init__(self,'Xml parse  error')
        self.filename = filename
        self.errorcode = errorcode
        self.position = position

    def __str__(self) -> str:
        return ('XML parse error in ' + self.filename + ' (errorcode: '
                    + str(self.errorcode) + ') at position  '
                    + str(self.position))

class CHJOSErrorInAnalyzer(CHJError):

    def __init__(self, 
            cmd: str, 
            e: Exception) -> None:
        CHJError.__init__(self,'OS Error in analyzer: ' + str(e))
        self.cmd = cmd
        self.error = e

    def __str__(self) -> str:
        return ('OS Error in command\n' + str(self.cmd) + '\n' + str(self.error) + '\n'
                    + 'Please check your platform settings in Config.py')

class CHJProcessError(CHJError):

    def __init__(self,
            cmd: str,
            e : Exception) -> None:
        CHJError.__init__(self,'Process Error in analyzer: ' + str(e))
        self.cmd = cmd
        self.error = e

    def __str__(self) -> str:
        return ('Process Error in command\n' + self.cmd + '\n' + str(self.error))

class CHJCodeHawkAnalyzerError(CHJError):

    def __init__(self,
            cmd: str,
            result: int) -> None:
        CHJError.__init__(self,'CodeHawk Java Analyzer returned result: ' + str(result))
        self.cmd = cmd
        self.result = result

    def __str__(self) -> str:
        return ('CodeHawk Java Analyzer result not zero: ' + str(self.result)
                    + '\n' + str(self.cmd))

class CHJNoAnalysisResultsFoundError(CHJError):

    def __init__(self, path: str) -> None:
        CHJError.__init__(self,'No analysis results found in ' + path)
        self.path = path

    def __str__(self) -> str:
        return ('No analysis results found in ' + self.path
                    + '\nPlease run the analyzer first (chj_analyze.py)')

class  CHJTaintTrailNotFoundError(CHJError):

    def __init__(self,
            path: str,
            filename: str,
            trailfilenames: List[str]) -> None:
        CHJError.__init__(self,'Taint trail file ' + filename + ' not found')
        self.filename = filename
        self.trailfilenames = trailfilenames

    def __str__(self) -> str:
        lines = []
        lines.append('Taint trail: ' + os.path.basename(self.filename) + ' not found')
        if len(self.trailfilenames) > 0:
            lines.append('trail files found: ')
            lines.append('-' * 80)
            for f in  self.trailfilenames:
                lines.append('  ' + f)
        return '\n'.join(lines)

class CHJPlatformNotFoundError(CHJError):

    def __init__(self, platform: str) -> None:
        CHJError.__init__(self,'Platform ' + platform + ' not found in config.platforms')

class CHJEngagementsRepoNotFoundError(CHJError):

    def __init__(self) -> None:
        CHJError.__init__(self,'STAC Engagements repository not found')

    def __str__(self) -> str:
        return ('STAC Engagements repository not found. Please set its '
                    + ' location in your util/ConfigLocal.py file')

class CHJEngagementsDirectoryNotFoundError(CHJError):

    def __init__(self, repodir: str) -> None:
        CHJError.__init__(self,'STAC Engagements directory not found at ' + repodir)
        self.repodir = repodir

    def __str__(self) -> str:
        return ('STAC Engagements directory not found at ' + self.repodir)


class CHJEngagementApplicationNotFoundError(CHJError):

    def __init__(self, 
            name: str, 
            names: Dict[str, List[str]]) -> None:
        CHJError.__init__(self,'No engagement application found with name ' + name)
        self.name = name
        self.names = names

    def __str__(self) -> str:
        lines = []
        lines.append('No engagment application found with name ' + self.name)
        lines.append('Applications available:')
        lines.append('-' * 80)
        for e in self.names:
            lines.append(e)
            for app in self.names[e]:
                lines.append('  ' + app)
        lines.append('-' * 80)
        return '\n'.join(lines)
            
class CHJEngagementDataNoDependenciesError(CHJError):

    def __init__(self, appname: str) -> None:
        CHJError.__init__(self,'Dependencies are missing in record for ' + appname)
        self.appname = appname

    def __str__(self) -> str:
        return ('Record for application ' + self.appname + ' is incomplete: '
                    + ' dependencies are missing')

def get_xnode(
        filename: str,
        rootnode: str,
        desc : str,
        show: bool = True) -> Optional[ET.Element]:
    if os.path.isfile(filename):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            node = root.find(rootnode)
            if node is not None:
                return node
            else:
                raise CHJError(desc + ' missing from ' + filename)
        except ET.ParseError as e:
            raise CHJXmlParseError(filename, e.code, e.position)
    elif show:
        raise CHJFileNotFoundError(filename)
    else:
        return None

# ----------------------------------------------  check presence of analyzer --

def check_analyzer() -> None:
    analyzer = config.analyzer
    if analyzer is None:
        raise CHJAnalyzerNotSetError()
    if not os.path.isfile(analyzer):
        raise CHJAnalyzerNotFoundError(config.analyzer)

def check_gui() -> None:
    gui = config.gui
    if gui is None:
        raise CHJGuiNotSetError()
    if not os.path.isfile(gui):
        raise CHJGuiNotFoundError(config.gui)

def check_analysisdir(path: str) -> None:
    if not os.path.isdir(os.path.join(path,'chanalysis')):
        raise CHJNoAnalysisResultsFoundError(path)

def check_file(filename: str) -> None:
    if not os.path.isfile(filename):
        raise CHJFileNotFoundError(filename)

def check_dir(path: str) -> None:
    if not os.path.isdir(path):
        raise CHJDirectoryNotFoundError(path)

# ----------------------------------------------------- method_index file --

def get_method_index_filename(path: str) -> str:
    return os.path.join(path,'methodindex.json')

def has_method_index(path: str) -> bool:
    return os.path.isfile(get_method_index_filename(path))

def get_method_index(path: str) -> Any:
    if has_method_index(path):
        filename = get_method_index_filename(path)
        with open(filename) as fp:
            return json.load(fp)
    print('No method index found in ' + str(path))

def save_method_index(path: str, methodindex: object) -> None:
    filename = get_method_index_filename(path)
    with open(filename,'w') as fp:
        json.dump(methodindex,fp)

# ------------------------------------------------------ various utilities --

T = TypeVar('T', str, int, float)
def safe_get(xnode: ET.Element, name: str, message: str, type: Type[T]) -> T:
    node = xnode.get(name)
    if node is None:
        raise CHJError(message)
    else:
        return type(node)

def safe_find(xnode: ET.Element, name: str, message: str) -> ET.Element:
    node = xnode.find(name)
    if node is None:
        raise CHJError(message)
    else:
        return node

def transform_methodname(mname: str) -> str:
    mname = mname.replace('<init>','__init__')
    mname = mname.replace('<clinit>','__clinit__')
    if mname.startswith('lambda'): mname = mname.replace('$','__')
    return mname


# ----------------------------------------------------- directory accesses --

def get_analysisdir(path: str) -> str:
    return os.path.join(path,'chanalysis')

def get_analysisdatadir(path: str) -> str:
    return os.path.join(get_analysisdir(path),'chdata')

def get_analysis_app_dir(path: str) -> str:
    return os.path.join(get_analysisdir(path),'chapp')

def get_costdir(path: str) -> str:
    analysisdir = get_analysisdir(path)
    costdir = os.path.join(analysisdir,'chcost')
    if not os.path.isdir(costdir):
        os.chdir(analysisdir)
        os.mkdir('chcost')
    return os.path.join(analysisdir,'chcost')

def get_costsupportdir(path: str) -> str:
    costdir = get_costdir(path)
    costsupportdir = os.path.join(costdir,'support')
    if not os.path.isdir(costsupportdir):
        os.chdir(costdir)
        os.mkdir('support')
    return os.path.join(costdir,'support')

def get_userdatadir(path: str) -> str:
    userdatadir = os.path.join(path,'chuserdata')
    if not os.path.isdir(userdatadir):
        os.chdir(path)
        os.mkdir('chuserdata')
    return os.path.join(path,'chuserdata')

# --------------------------------------------------------------- chdata ---
def get_datadictionary_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'dictionary.xml')

def get_datadictionary_xnode(path: str) -> ET.Element:
    filename = get_datadictionary_filename(path)
    return cast(ET.Element, get_xnode(filename,'dictionary','Dictionary file'))

def get_datacallgraph_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'callgraph.xml')

def get_datacallgraph_xnode(path: str) -> ET.Element:
    filename = get_datacallgraph_filename(path)
    return cast(ET.Element, get_xnode(filename,'callgraph','Callgraph file'))

def get_jterm_dictionary_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'jt_dictionary.xml')

def get_jterm_dictionary_xnode(path: str) -> ET.Element:
    filename = get_jterm_dictionary_filename(path)
    return cast(ET.Element, get_xnode(filename,'dictionary','Jterm dictionary file'))

def get_dataclassnames_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'classnames.xml')

def get_dataclassnames_xnode(path: str) -> ET.Element:
    filename = get_dataclassnames_filename(path)
    return cast(ET.Element, get_xnode(filename,'classnames','Classnames file'))

def get_datamissingitems_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'missing_items.xml')

def get_datamissingitems_xnode(path: str) -> ET.Element:
    filename = get_datamissingitems_filename(path)
    return cast(ET.Element, get_xnode(filename,'missing-items','Missing items file'))

def get_datasignatures_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'signatures.xml')

def get_datasignatures_xnode(path: str) -> ET.Element:
    filename = get_datasignatures_filename(path)
    return cast(ET.Element, get_xnode(filename,'signatures','Signatures file'))

def get_data_taint_origins_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'taintorigins.xml')

def get_data_taint_origins_xnode(path: str) -> Optional[ET.Element]:
    filename = get_data_taint_origins_filename(path)
    return get_xnode(filename,'taint-origins','Taint origins file',show=False)

def get_data_taint_trail_filename(path: str, id: int) -> str:
    return os.path.join(get_analysisdatadir(path),'tainttrails_' + str(id) + '.xml')

def list_data_taint_trail_filenames(path: str) -> List[str]:
    datapath = get_analysisdatadir(path)
    filenames = os.listdir(datapath)
    return [ f for f in filenames if f.startswith('tainttrails_') ]

def get_data_taint_trail_xnode(path: str, id: int) -> ET.Element:
    filename = get_data_taint_trail_filename(path,id)
    if os.path.isfile(filename):
        return cast(ET.Element, get_xnode(filename,'taint-trails','Taint trail file'))
    files = list_data_taint_trail_filenames(path)
    raise CHJTaintTrailNotFoundError(path,filename,files)

def get_timecost_diagnostics_filename(path: str) -> str:
    return os.path.join(get_analysisdatadir(path),'timecost_diagnostics.xml')

def get_timecost_diagnostics_xnode(path: str) -> ET.Element:
    filename = get_timecost_diagnostics_filename(path)
    return cast(ET.Element, get_xnode(filename,'time-cost-diagnostics','missing cost expressions'))

# ------------------------------------------------------------------ chapp ---   

def get_app_packagedir(path: str, package: str) -> str:
    sumdir = get_analysis_app_dir(path)
    return os.path.join(sumdir,package.replace('.','/'))

def get_app_class_filename(
        path: str,
        package: str,
        cname: str) -> str:
    sumdir = get_app_packagedir(path,package)
    return os.path.join(sumdir, cname + '.xml')

def get_app_class_xnode(
        path: str,
        package: str,
        cname: str) -> Optional[ET.Element]:
    try:
        filename = get_app_class_filename(path,package,cname)
        return cast(ET.Element, get_xnode(filename,'class','Class file'))
    except:
        print(package + '.' + cname + ' not found')
        return None

def get_app_classdir(
        path: str,
        package: str,
        cname: str) -> str:
    cname = cname.replace('$', '__dollarsign__')
    sumdir = get_app_packagedir(path,package)
    return os.path.join(sumdir,cname)

def get_app_methods_filename(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str,
        suffix: str) -> str:
    classdir = get_app_classdir(path,package,cname)
    mname = transform_methodname(mname)
    return os.path.join(classdir,mname + '_' + str(id) + '_' + suffix + '.xml')

def get_app_methodsbc_filename(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> str:
    return get_app_methods_filename(path,package,cname,mname,id,'bc')

def get_app_methodsbc_xnode(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> ET.Element:
    filename = get_app_methodsbc_filename(path,package,cname,mname,id)
    return cast(ET.Element, get_xnode(filename,'method','Method file'))

def get_app_methodsinvs_filename(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> str:
    return get_app_methods_filename(path,package,cname,mname,id,'invs')

def get_app_methodsinvs_xnode(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> ET.Element:
    filename = get_app_methodsinvs_filename(path,package,cname,mname,id)
    return cast(ET.Element, get_xnode(filename,'method','Method file'))

def get_app_methodsloops_filename(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> str:
    return get_app_methods_filename(path,package,cname,mname,id,'loops')

def get_app_methodsloops_xnode(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> ET.Element:
    filename = get_app_methodsloops_filename(path,package,cname,mname,id)
    return cast(ET.Element, get_xnode(filename,'method','Method file'))

def get_app_methodstaint_filename(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> str:
    return get_app_methods_filename(path,package,cname,mname,id,'taint')

def get_app_methodstaint_xnode(
        path: str,
        package: str,
        cname: str,
        mname: str,
        id: str) -> Optional[ET.Element]:
    filename = get_app_methodstaint_filename(path,package,cname,mname,id)
    return get_xnode(filename,'method','Method file',show=False)

# ----------------------------------------------------------------- chcost ---

def get_costdefaultmodel_filename(path: str) -> str:
    costdir = get_costdir(path)
    return os.path.join(costdir,'defaultcostmodel.xml')

def get_costpackagedir(path: str, package: str) -> str:
    costdir = get_costdir(path)
    return os.path.join(costdir,package.replace('.','/'))

def get_costclass_filename(
        path: str,
        package: str,
        cname: str) -> str:
    costdir = get_costpackagedir(path,package)
    return os.path.join(costdir, cname + '.xml')

def get_costclass_xnode(
        path: str,
        package: str,
        cname: str) -> ET.Element:
    filename = get_costclass_filename(path,package,cname)
    return cast(ET.Element, get_xnode(filename,'class','Class cost file'))

def get_costsupportpackagedir(path : str, package: str) -> str:
    costsupdir = get_costsupportdir(path)
    return os.path.join(costsupdir,package.replace('.','/'))

def get_costsupportclass_filename(
        path: str,
        package: str,
        cname: str) -> str:
    costsupdir = get_costsupportpackagedir(path,package)
    return os.path.join(costsupdir, cname + '.xml')

def get_costsupportclass_xnode(
        path: str,
        package: str,
        cname: str) -> ET.Element:
    filename = get_costsupportclass_filename(path,package,cname)
    return cast(ET.Element, get_xnode(filename,'class','Class cost support file'))

# -------------------------------------------------------------- chuserdata ---

def get_costmodel_constants_filename(path: str) -> str :
    return os.path.join(get_userdatadir(path),'constants.xml')

def get_costmodel_constants_xnode(path : str) -> ET.Element:
    filename = get_costmodel_constants_filename(path)
    return cast(ET.Element, get_xnode(filename,'constants','Cost constants file'))

def get_userdataclass_filename(
        path: str,
        package: str,
        cname: str) -> str:
    userdir = get_userdatadir(path)
    if package == '':
        return os.path.join(userdir,cname + '.xml')
    else:
        pckdir = os.path.join(userdir,package.replace('.','/'))
        if not os.path.isdir(pckdir):
            os.makedirs(pckdir)
        return os.path.join(pckdir,cname + '.xml')

def get_userdataclass_xnode(
        path: str,
        package: str,
        cname: str) -> Optional[ET.Element]:
    filename = get_userdataclass_filename(path,package,cname)
    return get_xnode(filename,'class','User class file',show=False)

def save_userdataclass_file(
        path: str,
        package: str,
        cname: str,
        xnode: ET.Element) -> None:
    filename = get_userdataclass_filename(path,package,cname)
    with open(filename,'w') as fp:
        fp.write(UX.doc_to_pretty(ET.ElementTree(xnode)))

# ------------------------------------------------------------- chreports ------

def get_engagement_reports_dir(path: str) -> str:
    if path.endswith('challenge_program'):
        result = path[:-17]
    elif path.endswith('challenge_program\\'):
        result = path[:-18]
    if result is not None:
        reportsdir = os.path.join(result,'chreports')
        if not os.path.isdir(reportsdir):
            print('Creating reports directory ' + reportsdir)
            os.makedirs(reportsdir)
        return reportsdir

# ------------------------------------------------------------- Engagements ----

def get_engagements_repo_path() -> str:
    if config.stacrepodir is None:
        raise CHJEngagementsRepoNotFoundError()
    if os.path.isdir(config.stacrepodir):
        return config.stacrepodir
    raise CHJEngagementsDirectoryNotFoundError(config.stacrepodir)

def get_engagements_directory() -> str:
    path = get_engagements_repo_path()
    if os.path.isdir(path):
        return path
    raise CHJDirectoryNotFoundError(path)

def get_engagements_data_filename() -> str:
    path = get_engagements_repo_path()
    filename = os.path.join(path,'engagements.json')
    if os.path.isfile(filename):
        return filename
    raise CHJFileNotFoundError(filename)

def get_engagements_data_file() -> Dict[str, Any]:
    filename = get_engagements_data_filename()
    try:
        with open(filename,'r') as fp:
            return json.load(fp)
    except ValueError as e:
        raise CHJJSONParseError(filename,e)

def get_engagement_from_name(name: str) -> str:
    engagements = get_engagements_data_file()
    for engg in engagements:
        if name in engagements[engg]['apps']:
            return engg
    else:
        names : Dict[str, List[Any]] = {}
        for engg in engagements:
            names[engg] = []
            for app in engagements[engg]['apps']:
                names[engg].append(app)
        raise CHJEngagementApplicationNotFoundError(name,names)

def check_challenge_jars_presence(path: str, jars: List[str]) -> None:
    for jar in jars:
        filename = os.path.join(path,jar)
        if os.path.isfile(filename): continue
        raise CHJFileNotFoundError(filename)

def get_engagement_app_data(appname: str) -> Tuple[str, Dict[str, Any]]:
    engg = get_engagement_from_name(appname)
    eepath = get_engagements_directory()
    engagements = get_engagements_data_file()
    epath = os.path.join(eepath,engg)
    if not os.path.isdir(epath):
        raise CHJDirectoryNotFoundError(epath)
    apppath = os.path.join(epath,appname)
    if not os.path.isdir(apppath):
        raise CHJDirectoryNotFoundError(apppath)
    challengepath = os.path.join(apppath,'challenge_program')
    if not os.path.isdir(challengepath):
        raise CHJDirectoryNotFoundError(challengepath)
    challengedata = engagements[engg]['apps'][appname]
    return (challengepath, challengedata)

def get_engagement_app_jars(name: str) -> Tuple[str, List[str]]:
    (path,appdata) = get_engagement_app_data(name)
    jars = appdata['jars']
    check_challenge_jars_presence(path,jars)
    return (path,jars)

def get_platform_data(platform: Optional[str]) -> Dict[str, str]:
    if platform is None:
        raise CHJError('Illegal platform: None')
    if platform in config.platforms:
        return config.platforms[platform]
    else:
        raise CHJPlatformNotFoundError(platform)

def get_jdksummaries_filename(platform: Optional[str]) -> str:
    if platform is None:
        jdkfilename: Optional[str] = config.jdksummaries
        if jdkfilename is None:
            raise CHJJDKSummariesLocationNotSetError(platform)
    else:
        platformdata = get_platform_data(platform)
        jdkfilename = platformdata.get('jdksummaries')
        path = platformdata.get('path', None)
        if jdkfilename is None or path is None:
            raise CHJJDKSummariesLocationNotSetError(platform)
        jdkfilename = os.path.join(path,jdkfilename)
        
    if os.path.isfile(jdkfilename):
        return jdkfilename
    else:
        raise CHJJDKSummariesFileNotFoundError(platform, jdkfilename)

def get_libsum_index(platform: Optional[str]) -> Tuple[str, Dict[str, Any]]:
    if platform is None:
        filename = config.libsumindex
        path = None
        if filename is None:
            raise CHJLibSumIndexLocationNotSetError(platform)
    else:
        platformdata = get_platform_data(platform)
        libsumindex = platformdata.get('libsumindex', None)
        path = platformdata.get('path', None)
        if libsumindex is None or path is None:
            raise CHJLibSumIndexLocationNotFoundError(platform)
        filename = os.path.join(path,libsumindex)
        
    if os.path.isfile(filename):
        with open(filename,'r') as fp:
            try:
                return (path, json.load(fp))
            except ValueError as e:
                raise CHJJSONParseError(filename,e)
    else:
        raise CHJLibSumIndexFileNotFoundError(platform, filename)

def get_lib_summary_jarfile_name(jarname: str, platform: Optional[str] = None) -> str:
    if platform is None and os.path.isfile(jarname):
        return jarname
    (path,libsumindex) = get_libsum_index(platform)
    if jarname in libsumindex:
        libloc = libsumindex[jarname]
        libpath = libloc['path']
        libjar = os.path.join(libpath,libloc['file'])
        if not path is None:
            libjar = os.path.join(path,libjar)
        else:
            libjar = os.path.join(config.summariesdir,libjar)
        if os.path.isfile(libjar):
            return libjar
        else:
            raise CHJLibrarySummaryJarNotFoundError(libjar)
        return os.path.join(libpath,libloc['file'])
    else:
        raise CHJLibraryJarNotFoundError(jarname)


def get_engagement_app_dependencies(appname: str) -> List[str]:
    (_,appdata) = get_engagement_app_data(appname)
    if 'dependencies' in appdata:
        return appdata['dependencies']
    raise CHJEngagementDataNoDependenciesError(appname)
            
def get_engagement_app_excludes(appname: str) -> List[str]:
    (_,appdata) = get_engagement_app_data(appname)
    if 'pkg-excludes' in appdata:
        return appdata['pkg-excludes']
    else:
        return []

def remove_analysis_dir(path: str) -> None:
    analysisdir = os.path.join(path,'chanalysis')
    if os.path.isdir(analysisdir):
        print('Removing ' + str(analysisdir) + ' ....')
        shutil.rmtree(analysisdir)
    else:
        print('No chanalysis directory present')

def get_engagement_help_message() -> str:
    lines = []
    lines.append('*' * 80)
    lines.append('Ensure the correct engagement directories are set in util/Config.py')
    lines.append('\nApplication data is available for:')
    appfile = get_engagements_data_file()
    if not appfile is None:
        for e in sorted(appfile):
            lines.append('\n' + e + ': ')
            for app in sorted(appfile[e]['apps']):
                lines.append('  ' + app)
    lines.append('*' * 80)
    return '\n'.join(lines)


# ---------------------------------------------------- Canonical applications ---

def getcanonicalappdata() -> Dict[str, Any]:
    appdata = {}
    datadir = config.appdatadir
    cappfile = os.path.join(os.path.join(datadir,'Canonical'),'applications.json')
    with open(cappfile) as fp:
        appdata = json.load(fp)
    return appdata['apps']
    
def getcanonicalapp(name: str) -> Tuple[str, List[str], str]:
    appdata = getcanonicalappdata()
    if not appdata is None and name in appdata:
        canonicaldir = config.canonicaldir
        path = os.path.join(os.path.join(canonicaldir,name),'challenge_program')
        jars = appdata[name]['jars']
        resource = appdata[name]['resource']
        return (path,jars,resource)
    else:
        print('*' * 80)
        print(name + ' is not a valid name of a canonical example')
        print('*' * 80)
        exit(1)

# ------------------------------------------------------------------------------
# Python API to access CodeHawk Java Analyzer analysis results
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
import datetime
import xml.etree.ElementTree as ET

from typing import List, Dict, Any, Optional

replacements = [ ('&', '&amp;'), ('<','&lt;'), ('>','&gt;'),
                 ('"','&quot;'), ('\'','&apos;') ]


def sanitizestring(s: str) -> str:
    for (a,b) in replacements:
        s = s.replace(a,b)
    return s
    # return s

def getixs(xnode: ET.Element) -> List[int]:
    ixs: Optional[str];
    if 'ixs' in xnode.attrib:
        ixs = xnode.get('ixs')
        assert ixs is not None;
        result = [ int(x) for x in ixs.split(',') ]
    else:
        result = []
        for ixl in xnode.findall('ix-list'):
            ixs = ixl.get('ixs')
            assert ixs is not None;
            result.extend( [ int(x) for x in ixs.split(',') ] )
    return result


def attributes_to_pretty(attr: Dict[str, str],indent: int=0) -> str:
    if len(attr) == 0:
        return ''
    if len(attr) > 4:
        lines = []
        for key in sorted(attr):
            attrvalue = sanitizestring(attr[key])
            lines.append(((' ' * (indent + 2)) + key + '="' + attrvalue + '"'))
        return ('\n' + '\n'.join(lines))
    else:
        return (' ' + ' '.join(key + '="' + sanitizestring(attr[key]) + '"' 
                               for key in sorted(attr)))

def element_to_pretty(e: ET.Element, indent: int=0) -> List[str]:
    lines = []
    attrs = attributes_to_pretty(e.attrib,indent)
    ind = ' ' * indent
    if e.text is None or len(e.text.strip()) == 0:
        children = list(e)
        if children == []:
            lines.append(ind + '<' + e.tag + attrs + '/>\n')
            return lines
        else:
            lines.append(ind + '<' + e.tag + attrs + '>\n')
            for c in children:
                lines.extend(element_to_pretty(c,indent+2))
            lines.append(ind + '</' + e.tag + '>\n')
            return lines
    else:
        lines.append(ind + '<' + e.tag + attrs + '>' + e.text + '</' + e.tag + '>\n')
        return lines
                        
def doc_to_pretty(t: ET.ElementTree) -> str:
    lines = [ '<?xml version="1.0" encoding="UTF-8"?>\n' ]
    lines.extend(element_to_pretty(t.getroot()))
    return ''.join(lines)

def get_xml_header(info: str) -> ET.Element:
    root = ET.Element('codehawk-java-analyzer')
    tree = ET.ElementTree(root)
    header = ET.Element('header')
    header.set('info',info)
    header.set('time',str(datetime.datetime.now()))
    root.append(header)
    return root

def dict_to_xmlpretty(d: Dict[str, Any], dtag: str, etag: str, kname: str,vname: str) -> str:
    root = ET.Element('codehawk-java-analyzer')
    tree = ET.ElementTree(root)
    dnode = ET.Element(dtag)
    root.append(dnode)
    for (k,v) in d.items():
        enode = ET.Element(etag)
        enode.set(kname,str(k))
        enode.set(vname,str(v))
        dnode.append(enode)
    return(doc_to_pretty(tree))


def create_user_class_xnode(package: str, name: str) -> ET.Element:
    root = get_xml_header('class')
    cnode = ET.Element('class')
    cnode.set('name',name)
    cnode.set('package',package)
    ccnode = ET.Element('constructors')
    mmnode = ET.Element('methods')
    cnode.extend([ ccnode, mmnode ])
    root.append(cnode)
    return root

def get_flask_html_header(titletext: str) -> ET.Element:
    head = ET.Element('head')
    meta = ET.Element('meta')
    meta.set('charset','utf-8')
    title = ET.Element('title')
    title.text = titletext
    link1 = ET.Element('link')
    link1.set('rel','stylesheet')
    link1.set('href','https://www.w3schools.com/w3css/4/w3.css')
    link2 = ET.Element('link')
    link2.set('rel','stylesheet')
    link2.set('href','https://fonts.googleapis.com/icon?family=Material+Icons')
    link3 = ET.Element('link')
    link3.set('rel','stylesheet')
    link3.set('href',"{{ url_for('static',filename='algocomplexity.css') }}")
    head.extend([ meta, title, link1, link2, link3 ])
    return head


def html_to_pretty (body: ET.Element ,title: str) -> str:
    lines = [ '<!DOCTYPE HTML PUBLIC>' ]
    root = ET.Element('html')
    root.append(get_flask_html_header(title))
    root.append(body)
    lines.extend(element_to_pretty(root))
    return ''.join(lines)

# ------------------------------------------------------------------------------
# CodeHawk Java Analyzer
# Author: Andrew McGraw
# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
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

import chj.util.IndexedTable as IT

from typing import cast, Dict, Callable, List, Type, TypeVar, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.JTypeDictionary import JTypeDictionary

class JTypeDictionaryRecord(IT.IndexedTableValue):
    def __init__(
        self,
        jtd: "JTypeDictionary",
        index: int,
        tags: List[str],
        args: List[int]
    ) -> None:
        self.jtd = jtd
        self.index = index
        self.tags = tags
        self.args = args

__j_dictionary_record_types: Dict[Tuple[type, str], Type[JTypeDictionaryRecord]] = {}
JDiR = TypeVar('JDiR', bound=JTypeDictionaryRecord, covariant=True)

def j_dictionary_record_tag(tag_name: str) -> Callable[[Type[JDiR]], Type[JDiR]]:
    def handler(t: Type[JDiR]) -> Type[JDiR]:
        __j_dictionary_record_types[(t.__bases__[0], tag_name)] = t
        return t
    return handler

def construct_j_dictionary_record(
    jtd: "JTypeDictionary",
    index: int,
    tags: List[str],
    args: List[int],
    superclass: Type[JDiR]
) -> JDiR:
    if (superclass, tags[0]) not in __j_dictionary_record_types:
        raise Exception("unknown type: " + tags[0])
    instance = __j_dictionary_record_types[(superclass, tags[0])](jtd, index, tags, args)
    return cast(JDiR, instance)
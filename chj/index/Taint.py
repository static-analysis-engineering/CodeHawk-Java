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

import chj.index.TaintDictionaryRecord as TD

from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from chj.index.FieldSignature import ClassFieldSignature
    from chj.index.MethodSignature import ClassMethodSignature
    from chj.index.TaintDictionary import TaintDictionary

class TaintBase(TD.TaintDictionaryRecord):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TD.TaintDictionaryRecord.__init__(self,ttd,index,tags,args)
        self.ttd = ttd

    def __str__(self) -> str: return 'jdtaintbase'


class TStringConstant(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_string(self) -> str:
        if len(self.tags) > 0:
            return self.tags[0]
        else:
            return ''

    def get_string_length(self) -> int: return int(self.args[0])

    def is_hex(self) -> bool: return len(self.tags) > 1

    def __str__(self) -> str:
        if self.is_hex():
            return ('(' + str(self.get_string_length()) + '-char-string')
        else:
            return self.get_string()


class TSymbol(TaintBase):
    '''Symbolic value.'''

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_name(self) -> TStringConstant: 
        return self.ttd.get_string(int(self.args[1]))

    def get_attrs(self) -> List[TStringConstant]:
        if len(self.args) > 2:
            return [ self.ttd.get_string(int(x)) for x in self.args[2:] ]
        else:
            return []
                
    def get_seqnr(self) -> int: return int(self.args[0])

    def __str__(self) -> str:
        if len(self.args) > 2:
            attrs = '_' + '_'.join( [ str(x) for x in self.get_attrs() ])
        else:
            attrs = ''
        seqnr = self.get_seqnr()
        pseqnr = '_s:' + str(seqnr) if seqnr >= 0 else ''
        return str(self.get_name()) + str(attrs) + str(pseqnr)


class TVariable(TaintBase):
    '''CHIF variable.'''

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_name(self) -> str:
        return str(self.ttd.get_symbol(int(self.args[0])).get_name())

    def get_seqnr(self) -> int:
        return self.ttd.get_symbol(int(self.args[0])).get_seqnr()

    def get_type(self) -> str: return self.tags[0]

    def __str__(self) -> str: return (str(self.get_name()))


class TMethodTarget(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_targets(self) -> List["ClassMethodSignature"]:
        return [ self.ttd.jd.get_cms(int(x)) for x in self.args ]

    def __str__(self) -> str:
        tgts = self.get_targets()
        if len(tgts) == 0:
            return "no targets"
        else:
            return '\n'.join([ ('    ' + str(m)) for m in self.get_targets() ])

@TD.t_dictionary_record_tag("v")
class VariableTaint(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self) -> TVariable:
        return self.ttd.get_variable(int(self.args[1]))

    def __str__(self) -> str:
        return 'VAR:' + str(self.get_caller())  + ':' + str(self.get_variable())


@TD.t_dictionary_record_tag("f")
class FieldTaint(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_field(self) -> "ClassFieldSignature": 
        return self.ttd.jd.get_cfs(int(self.args[0]))

    def get_name(self) -> TStringConstant: 
        return self.ttd.get_string(int(self.args[1]))

    def get_caller(self) -> "ClassMethodSignature": 
        return self.ttd.jd.get_cms(int(self.args[2]))

    def get_pc(self) -> int: return int(self.args[3])

    def __str__(self) -> str:
        return ('FIELD: ' + str(self.get_caller()) + ' @ ' + str(self.get_pc()) + ' -- '
                    + str(self.get_field()) + ',' + str(self.get_name()))

@TD.t_dictionary_record_tag("c")
class CallerTaint(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_method(self) -> "ClassMethodSignature": 
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_name(self) -> TStringConstant: 
        return self.ttd.get_string(int(self.args[1]))

    def get_caller(self) -> "ClassMethodSignature": return self.ttd.jd.get_cms(int(self.args[2]))

    def get_pc(self) -> int: return int(self.args[3])

    def __str__(self) -> str:
        return ('CALLER:' + str(self.get_method()) + ',' + str(self.get_name()) + ','
                    + str(self.get_caller()) + ' @ ' + str(self.get_pc()))


@TD.t_dictionary_record_tag("t")
class TopTargetTaint(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_method_target(self) -> TMethodTarget:
        return self.ttd.get_method_target(int(self.args[0]))

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[1]))

    def get_pc(self) -> int: return int(self.args[2])

    def __str__(self) -> str:
        return ('TOP:' + str(self.get_caller()) + ' @ ' + str(self.get_pc())
                    + ' -- ' + str(self.get_method_target()))


@TD.t_dictionary_record_tag("s")
class StubTaint(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_stub(self) -> "ClassMethodSignature": 
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_caller(self) -> "ClassMethodSignature": return self.ttd.jd.get_cms(int(self.args[1]))

    def get_pc(self) -> int: return int(self.args[2])

    def __str__(self) -> str:
        return ('STUB:' + str(self.get_caller().get_aqname()) + ' @' + str(self.get_pc())
                    + ': ' + str(self.get_stub().get_aqname()))


class TaintOriginList(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_origins(self) -> List["TaintBase"]:
        return [ self.ttd.get_taint_origin(int(x)) for x in self.args ]

    def __str__(self) -> str:
        return '.\n'.join( [ str(x) for x in self.get_origins() ] )
        

class TaintedVariable(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_variable(self) -> TVariable:
        return self.ttd.get_variable(int(self.args[0]))

    def get_untrusted(self) -> TaintOriginList:
        return self.ttd.get_taint_origin_list(int(self.args[1]))

    def __str__(self) -> str:
        return (str(self.get_variable()) + ': [' + str(self.get_untrusted()) + ']')


class TaintedVariableIds(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_tainted_variables(self) -> List[TaintedVariable]:
        return [ self.ttd.get_tainted_variable(int(x)) for x in self.args ]

    def __str__(self) -> str:
        return '\n'.join([ str(x) for x in self.get_tainted_variables() ])


class TaintNodeBase(TaintBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintBase.__init__(self,ttd,index,tags,args)

    def is_call(self) -> bool: return False
    def is_var(self) -> bool: return False
    def is_conditional(self) -> bool: return False

    def dotlabel(self) -> str: return 'dot-label'


@TD.t_dictionary_record_tag("f")
class FieldTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_field(self) -> "ClassFieldSignature": return self.ttd.jd.get_cfs(int(self.args[0]))

    def dotlabel(self) -> str: return 'FIELD:' + str(self.get_field())

    def __str__(self) -> str: return ('FIELD(' + str(self.get_field()) + ')')


@TD.t_dictionary_record_tag("v")
class VariableTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def is_var(self) -> bool: return True

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self) -> TVariable:
        return self.ttd.get_variable(int(self.args[1]))

    def get_pc(self) -> int: return int(self.args[2])

    def dotlabel(self) -> str:
        return (self.get_caller().get_aqname() + ':' + str(self.get_variable())
                    + ' @' + str(self.get_pc()))

    def __str__(self) -> str:
        return ('VAR(' + str(self.get_caller().get_aqname()) + ': '
        + str(self.get_variable()) + ' @' + str(self.get_pc()) + ')')


@TD.t_dictionary_record_tag("q")
class VariableEqTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable1(self) -> TVariable:
        return self.ttd.get_variable(int(self.args[1]))

    def get_variable2(self) -> TVariable:
        return self.ttd.get_variable(int(self.args[2]))

    def dotlabel(self) -> str:
        return (self.get_caller().get_aqname() + ':' + str(self.get_variable1())
                    + ' = ' + str(self.get_variable2()))

    def __str__(self) -> str:
        return ('VAR-EQ(' + str(self.get_caller()) + ': ' + str(self.get_variable1())
                    + ',' + str(self.get_variable2()) + ')')


@TD.t_dictionary_record_tag("c")
class CallTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def is_call(self) -> bool: return True

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[2]))

    def get_callee(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[3]))

    def get_return_variable(self) -> Optional[TVariable]:
        index = int(self.args[4])
        if index < 0: return None
        return self.ttd.get_variable(index)

    def dotlabel(self) -> str:
        return self.get_caller().get_aqname() + ' calls ' + self.get_callee().get_aqname()

    def __str__(self) -> str:
        return 'CALL(' + str(self.get_caller()) + ' -> ' + str(self.get_callee()) + ')'


@TD.t_dictionary_record_tag("u")
class UnknownCallTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[2]))

    def get_pc(self) -> int: return int(self.args[1])

    def dotlabel(self) -> str:
        return ('UNKNOWN in ' + str(self.get_caller().get_aqname()) + ' @' + str(self.get_pc()))

    def __str__(self) -> str:
        return 'UNKNOWN_CALL(' + str(self.get_caller()) + ' @pc: ' + str(self.get_pc()) + ')'
        

@TD.t_dictionary_record_tag("o")
class ObjectFieldTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self) -> "ClassMethodSignature": return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self) -> TVariable: return self.ttd.get_variable(int(self.args[1]))

    def get_field(self) -> "ClassFieldSignature": return self.ttd.jd.get_cfs(int(self.args[2]))

    def get_pc(self) -> int: return int(self.args[3])

    def dotlabel(self) -> str:
        return ('OBJECT-FIELD: ' + str(self.get_field()) + ' in '
                    + str(self.get_caller()) + ' @' + str(self.get_pc()))

    def __str__(self) -> str:
        return ('OBJECT-FIELD(' + str(self.get_field()) + ',' + str(self.get_caller()) +
                    '@pc:' + str(self.get_pc()))


@TD.t_dictionary_record_tag("j")
class ConditionalTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_pc(self) -> int: return int(self.args[1])

    def is_conditional(self) -> bool: return True

    def dotlabel(self) -> str:
        return str(self.get_caller().get_aqname()) + ' @' + str(self.get_pc())

    def __str__(self) -> str:
        return ('CONDITIONAL(' + str(self.get_caller()) + '@pc' + str(self.get_pc()))


@TD.t_dictionary_record_tag("s")
class SizeTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self) -> "ClassMethodSignature":
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self) -> TVariable:
        return self.ttd.get_variable(int(self.args[1]))

    def get_pc(self) -> int: return int(self.args[2])

    def dotlabel(self) -> str:
        return ('SIZE: ' + str(self.get_caller().get_aqname()) + ', ' + str(self.get_variable())
                    + ' @' + str(self.get_pc()))
    
    def __str__(self) -> str:
        return ('SIZE(' + str(self.get_variable()) + ',' + str(self.get_caller()) + ','
                    + '@pc' + str(self.get_pc()))


@TD.t_dictionary_record_tag("r")
class RefEqualTaintNode(TaintNodeBase):

    def __init__(self,
            ttd: "TaintDictionary",
            index: int,
            tags: List[str],
            args: List[int]):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def __str__(self) -> str: return "REF-EQUAL"

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


import chj.index.JDictionaryRecord as JD

class TaintBase(JD.JDictionaryRecord):

    def __init__(self,ttd,index,tags,args):
        JD.JDictionaryRecord.__init__(self,index,tags,args)
        self.ttd = ttd

    def __str__(self): return 'jdtaintbase'


class TStringConstant(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_string(self):
        if len(self.tags) > 0:
            return self.tags[0]
        else:
            return ''

    def get_string_length(self): return int(self.args[0])

    def is_hex(self): return len(self.tags) > 1

    def __str__(self):
        if self.is_hex():
            return ('(' + str(self.get_string_length()) + '-char-string')
        else:
            return self.get_string()


class TSymbol(TaintBase):
    '''Symbolic value.'''

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_name(self): return self.ttd.get_string(int(self.args[1]))

    def get_attrs(self):
        if len(self.args) > 2:
            return [ self.jd.get_string(int(x)) for x in self.args[2:] ]
        else:
            return []
                

    def get_seqnr(self): return int(self.args[0])

    def __str__(self):
        if len(self.args) > 2:
            attrs = '_' + '_'.join( [ str(x) for x in self.get_attrs() ])
        else:
            attrs = ''
        seqnr = self.get_seqnr()
        pseqnr = '_s:' + str(seqnr) if seqnr >= 0 else ''
        return str(self.get_name()) + str(attrs) + str(pseqnr)


class TVariable(TaintBase):
    '''CHIF variable.'''

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_name(self):
        return str(self.ttd.get_symbol(int(self.args[0])).get_name())

    def get_seqnr(self):
        return self.ttd.get_symbol(int(self.args[0])).get_seqnr()

    def get_type(self): return self.tags[0]

    def __str__(self): return (str(self.get_name()))


class TMethodTarget(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_targets(self):
        return [ self.ttd.jd.get_cms(int(x)) for x in self.args ]

    def __str__(self):
        tgts = self.get_targets()
        if len(tgts) == 0:
            return "no targets"
        else:
            return '\n'.join([ ('    ' + str(m)) for m in self.get_targets() ])


class VariableTaint(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self):
        return self.ttd.get_variable(int(self.args[1]))

    def __str__(self):
        return 'VAR:' + str(self.get_caller())  + ':' + str(self.get_variable())


class FieldTaint(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_field(self): return self.ttd.jd.get_cfs(int(self.args[0]))

    def get_name(self): return self.ttd.get_string(int(self.args[1]))

    def get_caller(self): return self.ttd.jd.get_cms(int(self.args[2]))

    def get_pc(self): return int(self.args[3])

    def __str__(self):
        return ('FIELD: ' + str(self.get_caller()) + ' @ ' + str(self.get_pc()) + ' -- '
                    + str(self.get_field()) + ',' + str(self.get_name()))


class CallerTaint(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_method(self): return self.ttd.jd.get_cms(int(self.args[0]))

    def get_name(self): return self.ttd.get_string(int(self.args[1]))

    def get_caller(self): return self.ttd.jd.get_method(int(self.args[2]))

    def get_pc(self): return int(self.args[3])

    def __str__(self):
        return ('CALLER:' + str(self.get_method()) + ',' + str(self.get_name()) + ','
                    + str(self.get_caller()) + ' @ ' + str(self.get_pc()))


class TopTargetTaint(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_method_target(self):
        return self.ttd.get_method_target (int(self.args[0]))

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[1]))

    def get_pc(self): return int(self.args[2])

    def __str__(self):
        return ('TOP:' + str(self.get_caller()) + ' @ ' + str(self.get_pc())
                    + ' -- ' + str(self.get_method_target()))


class StubTaint(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_stub(self): return self.ttd.jd.get_cms(int(self.args[0]))

    def get_caller(self): return self.ttd.jd.get_cms(int(self.args[1]))

    def get_pc(self): return int(self.args[2])

    def __str__(self):
        return ('STUB:' + str(self.get_caller().get_aqname()) + ' @' + str(self.get_pc())
                    + ': ' + str(self.get_stub().get_aqname()))


class TaintOriginList(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_origins(self):
        return [ self.ttd.get_taint_origin(int(x)) for x in self.args ]

    def __str__(self):
        return '.\n'.join( [ str(x) for x in self.get_origins() ] )
        

class TaintedVariable(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_variable(self):
        return self.ttd.get_variable(int(self.args[0]))

    def get_untrusted(self):
        return self.ttd.get_taint_origin_list(int(self.args[1]))

    def __str__(self):
        return (str(self.get_variable()) + ': [' + str(self.get_untrusted()) + ']')


class TaintedVariableIds(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def get_tainted_variables(self):
        return [ self.ttd.get_tainted_variable(int(x)) for x in self.args ]

    def __str__(self):
        return '\n'.join([ str(x) for x in self.get_tainted_variables() ])


class TaintNodeBase(TaintBase):

    def __init__(self,ttd,index,tags,args):
        TaintBase.__init__(self,ttd,index,tags,args)

    def is_call(self): return False
    def is_var(self): return False
    def is_conditional(self): return False

    def dotlabel(self): return 'dot-label'


class FieldTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_field(self): return self.ttd.jd.get_cfs(int(self.args[0]))

    def dotlabel(self): return 'FIELD:' + str(self.get_field())

    def __str__(self): return ('FIELD(' + str(self.get_field()) + ')')


class VariableTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def is_var(self): return True

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self):
        return self.ttd.get_variable(int(self.args[1]))

    def get_pc(self): return int(self.args[2])

    def dotlabel(self):
        return (self.get_caller().get_aqname() + ':' + str(self.get_variable())
                    + ' @' + str(self.get_pc()))

    def __str__(self):
        return ('VAR(' + str(self.get_caller().get_aqname()) + ': '
        + str(self.get_variable()) + ' @' + str(self.get_pc()) + ')')


class VariableEqTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable1(self):
        return self.ttd.get_variable(int(self.args[1]))

    def get_variable2(self):
        return self.ttd.get_variable(int(self.args[2]))

    def dotlabel(self):
        return (self.get_caller().get_aqname() + ':' + str(self.get_variable1())
                    + ' = ' + str(self.get_variable2()))

    def __str__(self):
        return ('VAR-EQ(' + str(self.get_caller()) + ': ' + str(self.get_variable1())
                    + ',' + str(self.get_variable2()) + ')')


class CallTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def is_call(self): return True

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[2]))

    def get_callee(self):
        return self.ttd.jd.get_cms(int(self.args[3]))

    def get_return_variable(self):
        index = int(self.args[4])
        if index < 0: return 'none'
        return self.jd.get_variable(index)

    def dotlabel(self):
        return self.get_caller().get_aqname() + ' calls ' + self.get_callee().get_aqname()

    def __str__(self):
        return 'CALL(' + str(self.get_caller()) + ' -> ' + str(self.get_callee()) + ')'


class UnknownCallTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[2]))

    def get_pc(self): return int(self.args[1])

    def dotlabel(self):
        return ('UNKNOWN in ' + str(self.get_caller().get_aqname()) + ' @' + str(self.get_pc()))

    def __str__(self):
        return 'UNKNOWN_CALL(' + str(self.get_caller()) + ' @pc: ' + str(self.get_pc()) + ')'
        

class ObjectFieldTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self): return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self): return self.ttd.get_variable(int(self.args[1]))

    def get_field(self): return self.ttd.jd.get_cfs(int(self.args[2]))

    def get_pc(self): return int(self.args[3])

    def dotlabel(self):
        return ('OBJECT-FIELD: ' + str(self.get_field()) + ' in '
                    + str(self.get_caller()) + ' @' + str(self.get_pc()))

    def __str__(self):
        return ('OBJECT-FIELD(' + str(self.get_field()) + ',' + str(self.get_caller()) +
                    '@pc:' + str(self.get_pc()))


class ConditionalTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_pc(self): return int(self.args[1])

    def is_conditional(self): return True

    def dotlabel(self):
        return str(self.get_caller().get_aqname()) + ' @' + str(self.get_pc())

    def __str__(self):
        return ('CONDITIONAL(' + str(self.get_caller()) + '@pc' + str(self.get_pc()))


class SizeTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def get_caller(self):
        return self.ttd.jd.get_cms(int(self.args[0]))

    def get_variable(self):
        return self.ttd.get_variable(int(self.args[1]))

    def get_pc(self): return int(self.args[2])

    def dotlabel(self):
        return ('SIZE: ' + str(self.get_caller().get_aqname()) + ', ' + str(self.get_variable())
                    + ' @' + str(self.get_pc()))
    
    def __str__(self):
        return ('SIZE(' + str(self.get_variable()) + ',' + str(self.get_caller()) + ','
                    + '@pc' + str(self.get_pc()))


class RefEqualTaintNode(TaintNodeBase):

    def __init__(self,ttd,index,tags,args):
        TaintNodeBase.__init__(self,ttd,index,tags,args)

    def __str__(self): return "REF-EQUAL"

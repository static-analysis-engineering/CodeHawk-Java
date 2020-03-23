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

opstrings = {
    'mult': ' * ',
    'add': ' + ',
    'div': ' / ',
    'sub': ' - '
   }

relopstrings = {
    'ge': ' >= ',
    'le': ' <= ',
    'eq': ' = '
    }

def convert_op(s):
    if s in opstrings: return opstrings[s]
    return s

class JTermBase(JD.JDictionaryRecord):

    def __init__(self,jtd,index,tags,args):
        JD.JDictionaryRecord.__init__(self,index,tags,args)
        self.jtd = jtd

    def is_constant(self): return False

    def is_compound(self): return False

    def is_float_constant(self): return False

    def is_jterm_list(self): return False

    def is_zero(self): return False

    def is_one(self): return False

    def is_symbolic_expr(self): return False

    def is_symbolic_constant(self): return False

    def get_symbolic_dependencies(self): return []

    def has_symbolic_dependency(self,t): return False

    def to_float(self): return self

    def add(self,other):
        if other.is_zero(): return self
        if other.is_constant(): return other.add(self)
        if other.is_float_constant(): return other.add(self)
        return self.jtd.mk_arithmetic_jterm(self,other,'add')

    def div(self,other):
        if other.is_one(): return self        
        return self.jtd.mk_arithmetic_jterm(self,other,'div')

    def simplify(self): return self

    def __str__(self): return 'jdtermbase'


class JTStringConstant(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

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


class JTNumerical(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_value(self): return int(self.tags[0])

    def is_constant(self): return True

    def __str__(self): return str(self.get_value())


class JTFloat(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_value(self): return float(self.tags[0])

    def __str__(self): return self.tags[0]


class JTAuxiliaryVar(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_name(self): return str(self.jtd.get_string(self.args[0]))

    def is_symbolic_expr(self): return True

    def __str__(self): return 'aux:' + self.get_name()


class JTLocalVar(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_index(self): return int(self.args[0])

    def is_symbolic_expr(self): return True

    def __str__(self): return 'r:' + str(self.get_index())


class JTLoopCounter(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_index(self): return int(self.args[0])

    def is_symbolic_expr(self): return True        

    def __str__(self): return 'lc:' + str(self.get_index())


class JTConstant(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def equals(self,other):
        return other.is_constant() and self.index == other.index

    def is_zero(self): return self.get_value() == 0

    def is_one(self): return self.get_value() == 1

    def get_value(self):
        return self.jtd.get_numerical(int(self.args[0])).get_value()

    def to_float(self):
        return self.jtd.mk_float_constant(self.get_value())

    def add(self,other):
        if other.is_constant():
            v = self.get_value() + other.get_value()
            return self.jtd.mk_constant_jterm(v)
        if other.is_float_constant():
            return self.jtd.mk_float_constant(self.to_float().get_value() + other.get_value())
        else:
            return JTermBase.add(self,other)

    def div(self,other):
        if other.is_one(): return self
        if other.is_constant(): return self.to_float().div(other.to_float())
        if other.is_float_constant(): return self.to_float().div(other)
        return self.jtd.mk_arithmetic_jterm(self,other,'div')

    def is_constant(self): return True

    def simplify(self): return self.to_float()

    def __str__(self): return str(self.get_value())


class JTStaticFieldValue(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_cnix(self): return int(self.args[0])

    def get_class_name(self):
        self.jtd.jd.get_cn(self.get_cnix()).get_name()

    def get_field_name(self):
        return str(self.jtd.jd.ttd.get_string(int(self.args[0])))

    def is_symbolic_expr(self): return True        

    def __str__(self):
        return 'sf:' + str(self.get_class_name()) + '.' + self.get_field_name()


class JTObjectFieldValue(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_cmsix(self): return int(self.args[0])

    def get_method_name(self):
        if self.get_cmsix() == -1:
            return 'unknown-method'
        else:
            return self.jtd.jd.ttd.get_class_method_signature_data(self.get_cmsix()).methodname

    def get_varix(self): return int(self.args[1])

    def get_cnix(self): return int(self.args[2])

    def get_class_name(self):
        return self.jtd.jd.get_cn(self.get_cnix()).get_name()

    def get_field_name(self):
        return str(self.jtd.get_string(int(self.args[3])))

    def is_symbolic_expr(self): return True

    def __str__(self):
        return ('of:' + self.get_method_name() + ':' + self.get_class_name() + '.'
                    + self.get_field_name())


class JTBoolConstant(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_value(self):
        return True if int(self.args[0]) == 1 else False

    def __str__(self):
        return 'bc:' + str(self.get_value())


class JTFloatConstant(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_value(self):
        return self.jtd.get_float(int(self.args[0])).get_value()

    def is_float_constant(self): return True

    def div(self,other):
        if other.is_constant():
            return self.jtd.mk_float_constant(self.get_value() / other.to_float().get_value())
        if other.is_float_constant():
            return self.jtd.mk_float_constant(self.get_value() / other.get_value())
        return self.jtd.mk_arithmetic_jterm(self,other,'div')

    def add(self,other):
        if other.is_constant():
            return self.jtd.mk_float_constant(self.get_value() + other.to_float().get_value())
        if other.is_float_constant():
            return self.jtd.mk_float_constant(self.get_value() + other.get_value())
        return self.jtd.mk_arithmetic_jterm(self,other,'add')

    def __str__(self): return str(self.get_value())


class JTermStringConstant(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_string(self):
        return str(self.jd.get_string(int(self.args[0])))

    def __str__(self): return 'sc:' + str(self.get_string())


class JTArrayLength(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_jterm(self):
        return self.jtd.get_jterm(int(self.args[0]))

    def is_symbolic_expr(self): return True

    def __str__(self):
        return 'arraylength(' + str(self.get_jterm()) + ')'


class JTStringLength(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_jterm(self):
        return self.jtd.get_jterm(int(self.args[0]))

    def is_symbolic_expr(self): return True

    def __str__(self): return 'stringlength(' + str(self.get_jterm()) + ')'


class JTSize(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_jterm(self):
        return self.jtd.get_jterm(int(self.args[0]))

    def is_symbolic_expr(self): return True

    def __str__(self): return 'size(' + str(self.get_jterm()) + ')'


class JTSymbolicJTermConstant(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_name(self):
        return str(self.jtd.get_string(int(self.args[3])))

    def get_lower_bound(self):
        if self.has_lower_bound():
            return self.jd.get_numerical(int(self.args[1]))

    def get_upper_bound(self):
        if self.has_upper_bound():
            return self.jd.get_numerical(int(self.args[2]))

    def get_type(self):
        return self.jtd.jd.get_value_type(int(self.args[0]))

    def has_lower_bound(self): return (int(self.args[1]) > 0)

    def has_upper_bound(self): return (int(self.args[2]) > 0)        

    def __str__(self): return (self.get_name())


class JTSymbolicConstant(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_symbolic_jterm_constant(self):
        return self.jtd.get_symbolic_jterm_constant(int(self.args[0]))

    def get_name(self):
        return self.get_symbolic_jterm_constant().get_name()

    def get_type(self):
        return self.get_symbolic_jterm_constant().get_type()

    def is_symbolic_constant(self): return True

    def get_symbolic_dependencies(self): return [ self ]

    def has_symbolic_dependency(self,t): return self.index == t.index

    def __str__(self):
        return 'symc:' + str(self.get_symbolic_jterm_constant())


class JTArithmeticExpr(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_exp1(self):
        return self.jtd.get_jterm(int(self.args[0]))

    def get_exp2(self):
        return self.jtd.get_jterm(int(self.args[1]))

    def get_op(self): return self.tags[1]

    def is_compound(self): return True

    def get_symbolic_dependencies(self):
        return (self.get_exp1().get_symbolic_dependencies()
                    + self.get_exp2().get_symbolic_dependencies())

    def has_symbolic_dependency(self,t):
        return (self.get_exp1().has_symbolic_dependency(t)
                    or self.get_exp2().has_symbolic_dependency(t))

    def is_symbolic_expr(self):
        return (self.get_exp1().is_symbolic_expr()
                    or self.get_exp2().is_symbolic_expr())

    def simplify(self):
        jt1 = self.get_exp1().simplify()
        jt2 = self.get_exp2().simplify()
        if self.get_op() == 'div' and jt1.is_float_constant() and jt2.is_float_constant():
            return self.jtd.mk_float_constant(jt1.get_value() / jt2.get_value())
        if self.get_op() == 'div' and jt2.is_float_constant() and jt1.is_compound():
            op1 = jt1.get_op()
            jt11 = jt1.get_exp1().simplify()
            jt12 = jt1.get_exp2().simplify()
            if op1 == 'add':
                return self.jtd.mk_arithmetic_jterm(jt11.div(jt2).simplify(), jt12.div(jt2).simplify(), op1)
            if op1 =='mult' and jt11.is_float_constant():
                return self.jtd.mk_arithmetic_jterm(jt11.div(jt2).simplify(),jt12,'mult')
            if op1 == 'mult':
                return self.jtd.mk_arithmetic_jterm(jt11,jt12.div(jt2).simplify(),'mult')
            return self
        if self.get_op() == 'add' and jt1.is_float_constant() and jt2.is_float_constant():
            return self.jd.mk_float_constant(jt1.get_value() + jt2.get_value())
        if self.get_op() == 'add' and jt1.is_float_constant() and jt2.is_compound():
            op2 = jt2.get_op()
            jt21 = jt2.get_exp1().simplify()
            jt22 = jt2.get_exp2().simplify()
            if op2 == 'add' and jt21.is_float_constant():
                jt1new = self.jtd.mk_float_constant(jt1.get_value() + jt21.get_value())
                return self.jtd.mk_arithmetic_jterm(jt1new,jt22,'add').simplify()
            if op2 == 'add' and jt22.is_float_constant():
                jt1new = self.jtd.mk_float_constant(jt1.get_value() + jt22.get_value())
                return self.jtd.mk_arithmetic_jterm(jt1new,jt21,'add').simplify()
        return self.jtd.mk_arithmetic_jterm(jt1,jt2,self.get_op())
        
    def __str__(self):
        return ('(' + str(self.get_exp1()) + ' ' + convert_op(self.get_op())
                    + ' ' + str(self.get_exp2()) + ')')


class JTRelationalExpr(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_op(self): return self.tags[0]

    def get_exp1(self):
        return self.jtd.get_jterm(int(self.args[0]))

    def get_exp2(self):
        return self.jtd.get_jterm(int(self.args[1]))

    def __str__(self):
        return ('(' + str(self.get_exp1()) + relopstrings[self.get_op()]
                    + str(self.get_exp2()) + ')' )


class JTRelationalExprList(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_exprs(self):
        return [ self.jtd.get_relational_expr(int(x)) for x in self.args ]

    def __str__(self):
        return '\n'.join([ str(x) for x in self.get_exprs() ])


class JTermList(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def equals(self,other):
        return other.is_jterm_list() and self.index == other.index

    def get_jterms(self):
        return [ self.jtd.get_jterm(int(x)) for x in self.args ]

    def get_length(self): return len(self.get_jterms())

    def is_jterm_list(self): return True

    def is_top(self): return len(self.args) == 0

    def is_constant(self):
        return len(self.args) == 1 and self.get_jterms()[0].is_constant()

    def get_constant(self):
        if self.is_constant(): return self.get_jterms()[0].get_value()

    def is_symbolic_expr(self):
        return any( [ x.is_symbolic_expr() for x in self.get_jterms() ])

    def get_symbolic_dependencies(self):
        return sum ( [ t.get_symbolic_dependencies() for t in self.get_jterms() ], [])

    def get_symbolic_expr(self):
        if self.is_symbolic_expr():
            return [ x for x in self.get_jterms() if x.is_symbolic_expr() ][0]

    def __str__(self): return ','.join( str(t) for t in self.get_jterms())


class JTermRange(JTermBase):

    def __init__(self,jtd,index,tags,args):
        JTermBase.__init__(self,jtd,index,tags,args)

    def get_lower_bounds(self):
        return self.jtd.get_jterm_list(int(self.args[0]))

    def get_upper_bounds(self):
        return self.jtd.get_jterm_list(int(self.args[1]))

    def get_ub_symbolic_dependencies(self):
        return self.get_upper_bounds().get_symbolic_dependencies()

    def is_top(self):
        return self.get_lower_bounds().is_top() and self.get_upper_bounds().is_top()

    def is_value(self):
        if self.get_lower_bounds().is_constant() and self.get_upper_bounds().is_constant():
            return self.get_lower_bounds().equals(self.get_upper_bounds())

    def is_float_range(self): return False
    '''
        if self.get_lower_bounds().get_length() == 1 and self.get_upper_bounds().get_length() == 1:
            lb = self.get_lower_bounds().get_jterms()[0].simplify()
            ub = self.get_upper_bounds().get_jterms()[0].simplify()
            return lb.is_float_constant() and ub.is_float_constant()
        return False
    '''

    def get_float_range(self):
        if self.is_float_range():
            lb = self.get_lower_bounds().get_jterms()[0].simplify()
            ub = self.get_upper_bounds().get_jterms()[0].simplify()
            return (lb,ub)

    def get_value(self):
        if self.is_value(): return self.get_lower_bounds().get_constant()

    def is_range(self):
        return (self.get_lower_bounds().is_constant()
                    and self.get_upper_bounds().is_constant())

    def is_ub_open_range(self):
        return (self.get_lower_bounds().is_constant()
                    and self.get_upper_bounds().is_top())

    def is_lb_open_range(self):
        ubs = self.get_lower_bounds().is_top and self.get_upper_bounds().is_constant()

    def get_range(self):
        if self.is_range():
            return (self.get_lower_bounds().get_constant(),
                        self.get_upper_bounds().get_constant())

    def get_ub_open_range(self):
        if self.is_ub_open_range(): return self.get_lower_bounds().get_constant()

    def get_lb_open_range(self):
        if self.is_lb_open_range(): return self.get_upper_bounds().get_constant()

    def is_symbolic_expr(self):
        return self.get_upper_bounds().is_symbolic_expr()

    def get_symbolic_expr(self):
        if self.is_symbolic_expr(): return self.get_upper_bounds().get_symbolic_expr()

    def __str__(self):
        if self.is_top(): return 'T'
        if self.is_value(): return str(self.get_value())
        if self.is_range():
            (lb,ub) = self.get_range()
            return '[' + str(lb) + '; ' + str(ub) + ']'
        if self.is_ub_open_range():
            return '[' + str(self.get_ub_open_range()) + '; ->'
        if self.is_lb_open_range():
            return '<- ; ' + str(self.get_lb_open_range()) + ']'
        if self.is_symbolic_expr():
            return str(self.get_symbolic_expr())
        lb = str(self.get_lower_bounds())
        ub = str(self.get_upper_bounds())
        if lb == ub:
            return lb
        else:
            return 'lb:' + str(self.get_lower_bounds()) + '\n   ub:' + str(self.get_upper_bounds())



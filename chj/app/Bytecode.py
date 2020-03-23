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

class BcBase(JD.JDictionaryRecord):

    def __init__(self,bcd,index,tags,args):
        JD.JDictionaryRecord.__init__(self,index,tags,args)
        self.bcd = bcd                               # BcDictionary
        self.jd = self.bcd.jd                        # DataDictionary
        self.tpd = self.jd.tpd                       # JTypeDictionary
        self.jtd = self.jd.jtd                       # JTermDictionary

    def __str__(self): return 'javaclass-dictionary-record'

class BcPcList(BcBase):

    def __init__(self,bcd,index,tags,args):
        BcBase.__init__(self,bcd,index,tags,args)

    def get_pcs(self): return [ int(x) for x in self.args ]

    def __str__(self): return 'pcs:' + ','.join([str(x) for x in self.get_pcs() ])


class BcSlot(BcBase):

    def __init__(self,bcd,index,tags,args):
        BcBase.__init__(self,bcd,index,tags,args)

    def get_level(self): return int(self.args[2])

    def get_types(self):
        print(str(self.args))
        return [ self.tpd.get_value_type(int(x)) for x in self.args[4:] ]

    def get_slot_value(self): return self.jterms.get_jterm_range(int(self.args[3]))

    def get_src_pcs(self):
        srctag = self.tags[0]
        if srctag == 'n': return []
        if srctag == 's': return [ int(self.args[0]) ]
        if srctag == 'm': return self.bcdict.get_pc_list(int(self.args[0])).get_pcs()

    def get_dst_pcs(self):
        dsttag = self.tags[1]
        if dsttag == 'n': return []
        if dsttag == 's': return [ int(self.args[1]) ]
        if dsttag == 'm': return self.bcdict.get_pc_list(int(self.args[1])).get_pcs()

    def __str__(self):
        return (str(self.get_level()) + ':' + ','.join([ str(x) for x in self.get_types()])
                    + '; src-pcs:' + ','.join([ str(x) for x in self.get_src_pcs() ])
                    + '; dst-pcs:' + ','.join([ str(x) for x in self.get_dst_pcs() ]))


class BcSlotList(BcBase):

    def __init__(self,bcd,index,tags,args):
        BcBase.__init__(self,bcd,index,tags,args)

    def get_slots(self): return [ self.bcd.get_slot(int(x)) for x in self.args ]

    def __str__(self):
        lines = []
        for s in self.get_slots(): lines.append(' '.rjust(28) + str(s))
        return '\n'.join(lines)


class JBytecodeBase(BcBase):

    def __init__(self,bcd,index,tags,args):
        BcBase.__init__(self,bcd,index,tags,args)

    def opcstr(self,s): return s.ljust(20)

    def is_call(self): return False

    def is_load_string(self): return False

    def is_put_static(self): return False

    def is_put_field(self): return False

    def is_get_static(self): return False

    def is_get_field(self): return False

    def is_object_created(self): return False

    def is_array_created(self): return False

    def is_multi_array_created(self): return False

    def __str__(self): return 'bc: ' + self.tags[0]

class BcInstruction(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr(self.tags[0])


class BcLoad(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_var_index(self): return int(self.args[0])

    def get_type(self): return self.tags[1]

    def __str__(self):
        return self.opcstr('load_' + str(self.get_var_index())) + str(self.get_type())


class BcStore(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_var_index(self): return int(self.args[0])

    def get_type(self): return self.tags[1]

    def __str__(self):
        return self.opcstr('store_' + str(self.get_var_index())) + str(self.get_type())


class BcIInc(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_increment(self): return int(self.args[0])

    def get_var_index(self): return int(self.args[1])

    def __str__(self):
        return self.opcstr('iinc') + str(self.get_var_index()) + ', ' + str(self.get_increment())


class JBytecodeConstBase(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def is_load_constant(self): return True


class BcIntConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_value(self): return int(self.args[0])

    def __str__(self): return self.opcstr('iconst') + str(self.get_value())

class BcLongConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_value(self): return int(self.tags[1])

    def __str__(self): return self.opcstr('lconst') + str(self.get_value())


class BcFloatConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_value(self): return float(self.tags[1])

    def __str__(self): return self.opcstr('fconst') + str(self.get_value())

class BcDoubleConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_value(self): return float(self.tags[1])

    def __str__(self): return self.opcstr('dconst') + str(self.get_value())

class BcByteConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_value(self): return int(self.args[0])

    def __str__(self): return self.opcstr('bconst') + str(self.get_value())

class BcShortConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_value(self): return int(self.args[0])

    def __str__(self): return self.opcstr('sconst') + str(self.get_value())

class BcStringConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_string_constant(self): return self.tpd.get_string(int(self.args[0]))

    def is_load_string(self): return True

    def __str__(self): return self.opcstr('ldc') + str(self.get_string_constant())

class BcClassConst(JBytecodeConstBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConstBase.__init__(self,bcd,index,tags,args)

    def get_class(self): return self.tpd.get_object_type(int(self.args[0]))

    def __str__(self): return self.opcstr('ldc') + str(self.get_class())

class JBytecodeArithmeticBase(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tags[1]

    def is_arithmetic_instruction(self): return True


class BcAdd(JBytecodeArithmeticBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeArithmeticBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('add') + str(self.get_type())

class BcSub(JBytecodeArithmeticBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeArithmeticBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('sub') + str(self.get_type())

class BcMult(JBytecodeArithmeticBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeArithmeticBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('mult') + str(self.get_type())

class BcDiv(JBytecodeArithmeticBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeArithmeticBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('div') + str(self.get_type())

class BcRem(JBytecodeArithmeticBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeArithmeticBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('rem') + str(self.get_type())

class BcNeg(JBytecodeArithmeticBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeArithmeticBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('neg') + str(self.get_type())

class JBytecodeConditionalJumpBase(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_target_pc(self): return int(self.args[0])

    def __str__(self): return self.opcstr(self.tags[0]) + str(self.get_target_pc())


class BcIfEq(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)


class BcIfNe(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)


class BcIfLt(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)


class BcIfGe(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfGt(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfLe(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfNull(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfNonNull(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpEq(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpNe(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpLt(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpGe(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpGt(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpLe(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpAEq(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcIfCmpANe(JBytecodeConditionalJumpBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeConditionalJumpBase.__init__(self,bcd,index,tags,args)

class BcGoto(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_target_pc(self): return int(self.args[0])

    def __str__(self): return self.opcstr('goto') + str(self.get_target_pc())

class BcJsr(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_target_pc(self): return int(self.args[0])

    def __str__(self): return self.opcstr('jsr') + str(self.get_target_pc())

class BcRet(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_var_index(self): return int(self.args[0])

    def __str__(self): return self.opcstr('ret') + str(self.get_target_pc())

class BcTableSwitch(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('switch')

class BcLookupSwitch(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def __str__(self): return self.opcstr('lookup')

class BcNew(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_class(self): return self.jd.get_cn(int(self.args[0]))

    def is_object_created(self): return True

    def __str__(self): return self.opcstr('new') + str(self.get_class())

class BcNewArray(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tpd.get_value_type(int(self.args[0]))

    def is_object_created(self): return True

    def is_array_created(self): return True

    def __str__(self): return self.opcstr('newarray') + str(self.get_type())

class BcAMultiNewArray(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tpd.get_object_type(int(self.args[0]))

    def get_size(self): return int(self.args[1])

    def is_object_created(self): return True

    def is_array_created(self): return True

    def is_multi_array_created(self): return True

    def __str__(self):
        return self.opcstr('multinewarray') + str(self.get_type()) + ', ' + str(self.get_size())

class BcCheckCast(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tpd.get_object_type(int(self.args[0]))

    def __str__(self): return self.opcstr('checkcast') + str(self.get_type())

class BcInstanceOf(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tpd.get_object_type(int(self.args[0]))

    def __str__(self): return self.opcstr('instanceof') + str(self.get_type())

class BcFieldBase(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_cn(self): return self.jd.get_cn(int(self.args[0]))

    def get_field(self): return self.tpd.get_field_signature_data(int(self.args[1]))


class BcGetStatic(BcFieldBase):

    def __init__(self,bcd,index,tags,args):
        BcFieldBase.__init__(self,bcd,index,tags,args)

    def is_get_static(self): return True

    def __str__(self):
        return self.opcstr('getstatic') + str(self.get_cn()) + '.' + str(self.get_field())

class BcPutStatic(BcFieldBase):

    def __init__(self,bcd,index,tags,args):
        BcFieldBase.__init__(self,bcd,index,tags,args)

    def is_put_static(self): return True

    def __str__(self):
        return self.opcstr('putstatic') + str(self.get_cn()) + '.' + str(self.get_field())


class BcGetField(BcFieldBase):

    def __init__(self,bcd,index,tags,args):
        BcFieldBase.__init__(self,bcd,index,tags,args)

    def is_get_field(self): return True

    def __str__(self):
        return self.opcstr('getfield') + str(self.get_cn()) + '.' + str(self.get_field())


class BcPutField(BcFieldBase):

    def __init__(self,bcd,index,tags,args):
        BcFieldBase.__init__(self,bcd,index,tags,args)

    def is_put_field(self): return True

    def __str__(self):
        return self.opcstr('putfield') + str(self.get_cn()) + '.' + str(self.get_field())


class BcArrayLoad(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tags[1]

    def __str__(self): return self.opcstr('arrayload') + str(self.get_type())


class BcArrayStore(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tags[1]

    def __str__(self): return self.opcstr('arraystore') + str(self.get_type())
        

class BcInvokeBase(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_signature(self):
        return self.tpd.get_method_signature_data(int(self.args[1]))

    def is_call(self): return True


class BcInvokeVirtual(BcInvokeBase):

    def __init__(self,bcd,index,tags,args):
        BcInvokeBase.__init__(self,bcd,index,tags,args)

    def get_object(self): return self.tpd.get_object_type(int(self.args[0]))

    def __str__(self):
        return self.opcstr('invokevirtual') + str(self.get_object()) + '.' + str(self.get_signature())

class BcInvokeSpecial(BcInvokeBase):

    def __init__(self,bcd,index,tags,args):
        BcInvokeBase.__init__(self,bcd,index,tags,args)

    def get_class(self): return self.jd.get_cn(int(self.args[0]))

    def __str__(self):
        return self.opcstr('invokespecial') + str(self.get_class()) + '.' + str(self.get_signature())

class BcInvokeStatic(BcInvokeBase):

    def __init__(self,bcd,index,tags,args):
        BcInvokeBase.__init__(self,bcd,index,tags,args)

    def get_class(self): return self.jd.get_cn(int(self.args[0]))

    def __str__(self):
        return self.opcstr('invokestatic') + str(self.get_class()) + '.' + str(self.get_signature())


class BcInvokeInterface(BcInvokeBase):

    def __init__(self,bcd,index,tags,args):
        BcInvokeBase.__init__(self,bcd,index,tags,args)

    def get_class(self): return self.jd.get_cn(int(self.args[0]))

    def __str__(self):
        return self.opcstr('invokeinterface') + str(self.get_class()) + '.' + str(self.get_signature())

class BcInvokeDynamic(BcInvokeBase):

    def __init__(self,bcd,index,tags,args):
        BcInvokeBase.__init__(self,bcd,index,tags,args)

    def __str__(self):
        return self.opcstr('invokedynamic') + str(self.get_signature())

class BcReturn(JBytecodeBase):

    def __init__(self,bcd,index,tags,args):
        JBytecodeBase.__init__(self,bcd,index,tags,args)

    def get_type(self): return self.tags[1]

    def __str__(self): return self.opcstr('return') + str(self.get_type())

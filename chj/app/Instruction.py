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

from typing import Any, cast, List, Optional, TYPE_CHECKING

import chj.util.fileutil as UF

from chj.app.Bytecode import BcFieldBase
from chj.app.Bytecode import BcSlotList
from chj.app.Bytecode import BcStringConst
from chj.app.Bytecode import JBytecodeBase
from chj.app.Bytecode import BcInvokeBase

if TYPE_CHECKING:
    from chj.app.JavaMethod import JavaMethod
    from chj.index.MethodSignature import MethodSignature
    from chj.index.FieldSignature import FieldSignature
    from chj.index.CallgraphDictionary import CallgraphTargetBase
    from chj.index.Classname import Classname
    from chj.index.JType import StringConstant

class Instruction(object):

    def __init__(self,
            jmethod: "JavaMethod",
            pc: int,
            opc: "JBytecodeBase",
            exprstack: "BcSlotList",
            tgts: Optional["CallgraphTargetBase"] = None):
        self.jmethod = jmethod
        self.pc = pc
        self.opc = opc
        self.exprstack = exprstack
        self.tgts = tgts

    def has_targets(self) -> bool: return not (self.tgts is None)

    def get_targets(self) -> List[int]: 
        if self.has_targets():
            return cast("CallgraphTargetBase", self.tgts).cnixs
        else:
            raise UF.CHJError("Targets missing from Instruction")

    def get_cmsix_targets(self) -> List[int]:
        if self.opc.is_call():
            opc = cast("BcInvokeBase", self.opc)
            isig = opc.get_signature()
            if self.has_targets():
                return [ self.jmethod.jd.get_cmsix(cnix,isig.index) for cnix in self.get_targets() ]
            else:
                return []
        else:
            raise UF.CHJError(str(self.opc) + ' is not a call')

    def get_loop_depth(self) -> int:
        return self.jmethod.get_loop_depth(self.pc)

    def is_call(self) -> bool: return self.opc.is_call()

    def is_load_string(self) -> bool: return self.opc.is_load_string()

    def is_put_field(self) -> bool: return self.opc.is_put_field()

    def is_put_static(self) -> bool: return self.opc.is_put_static()

    def is_get_field(self) -> bool: return self.opc.is_get_field()

    def is_get_static(self) -> bool: return self.opc.is_get_static()

    def is_object_created(self) -> bool: return self.opc.is_object_created()

    def get_string_constant(self) -> "StringConstant": 
        if isinstance(self.opc, BcStringConst):
            return self.opc.get_string_constant()
        else:
            raise UF.CHJError(str(self.opc) + ' is not a string constant')

    def get_cn(self) -> "Classname":
        if isinstance(self.opc, BcFieldBase):
            return self.opc.get_cn()
        else:
            raise UF.CHJError(str(self.opc) + ' does not have a Classname')

    def get_signature(self) -> "MethodSignature":
        if isinstance(self.opc, BcInvokeBase):
            return self.opc.get_signature()
        else:
            raise UF.CHJError(str(self.opc) + ' does not have a signature')

    def get_field(self) -> "FieldSignature":
        if isinstance(self.opc, BcFieldBase):
            return self.opc.get_field()
        else:
            raise UF.CHJError(str(self.opc) + ' does not contain a field')

    def __str__(self) -> str: return str(self.opc)

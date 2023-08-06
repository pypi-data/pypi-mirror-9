#
# This file is part of pySMT.
#
#   Copyright 2015 Andrea Micheli and Marco Gario
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from pysmt.test import TestCase

from pysmt.shortcutes import BV, Symbol
from pysmt.typing import BITVECTOR


class TestBV(TestCase):
    def test_boolector_style(self):
        # Constants
        small = BV(1, 32)
        hexample = BV(0x16, 8)
        zero = BV(0, 128)
        s_one = BV(-1, 129) # Signed
        one = BV(1, 128)

        # Variables
        b = Symbol("b", BITVECTOR(128))

        not_zero    = BVNot(zero)
        neg_zero    = BVNeg(zero)

        # Reduction operations on bit vectors
        # MG: Shall we keep these?
        redor   = Redor(s_one)
        redxor  = Redxor(s_one)
        redand  = Redand(s_one)

        slicing = Slice(s_one, 8,8)

        uext    = Uext(small, 127)
        sext    = Sext(small, 127)

        res  = Dec(Inc(zero))
        self.assertEqual(zero, res)

        # MG: A key question is whether we want to keep automated
        # casting for Bit-Vectors of size 1 in operators such as
        # Implies, Iff.  This mixes theory and propositional. In the
        # same way as Equals and Iff are different.
        #
        # This might make the semantics of other boolean operators unclear:
        #   And(x,y) returns Either a bitvector or a boolean symbol.
        # locally the type is always clear.

        bit = BV(1, 1)
        with self.assertRaises(TypeError):
            Iff(bit, bit)

        with self.assertRaises(TypeError):
            Implies(bit, bit)

        res = BVXor(one, zero)
        res = BVAnd(one, zero)
        res = BVNand(one, zero)
        res = BVOr(one, zero)
        res = Nor(one, zero)
        res = Equals(one, zero)
        res = Plus(one, zero)
        res = Times(one, zero)

        res = Ult(one, zero)
        res = Slt(s_one, zero)
        res = Ulte(one, zero)
        res = Slte(s_one, zero)

        res = Ugt(one, zero)
        res = Sgt(s_one, zero)
        res = Ugte(one, zero)
        res = Sgte(s_one, zero)

        res = Sll(small, 5)
        res = Srl(small, 5)
        res = Sra(small, 5)
        res = Rol(small, 5)
        res = Ror(small, 5)

        res = Minus(one, small)
        res = Udiv(one, small)
        res = Urem(one, small)
        res = Sdiv(-one, small)
        res = Srem(-one, small)
        res = Smod(-one, small)

        # MG: Implement These?
        res = Uaddo(one, zero)
        res = Saddo(one, zero)
        res = Umulo(one, zero)
        res = Smulo(one, zero)
        res = Ssubo(one, zero)
        res = Sdivo(one, s_one)


        # Concatenation of bit vectors
        res = Concat(zero, one)
        self.assertEqual(res.bv_width() , zero.bv_width() + one.bv_width())

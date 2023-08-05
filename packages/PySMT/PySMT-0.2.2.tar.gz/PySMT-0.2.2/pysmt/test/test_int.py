#
# This file is part of pySMT.
#
#   Copyright 2014 Andrea Micheli and Marco Gario
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
from pysmt.shortcuts import *
from pysmt.typing import INT, REAL
from pysmt.test import TestCase, skipIfNoSolverAvailable

class TestLIA(TestCase):

    @skipIfNoSolverAvailable
    def test_eq(self):
        varA = Symbol("At", INT)
        varB = Symbol("Bt", INT)

        f = And(LT(varA, Plus(varB, Int(1))),
                GT(varA, Minus(varB, Int(1))))
        g = Equals(varA, varB)

        self.assertTrue(is_valid(Iff(f, g)),
                        "Formulae were expected to be equivalent")

    @skipIfNoSolverAvailable
    def test_lira(self):
        varA = Symbol("A", REAL)
        varB = Symbol("B", INT)

        with self.assertRaises(TypeError):
            f = And(LT(varA, Plus(varB, Real(1))),
                    GT(varA, Minus(varB, Real(1))))
            g = Equals(varB, Int(0))

            self.assertTrue(is_unsat(And(f, g, Equals(varA, Real(1.2)))),
                            "Formula was expected to be unsat")



if __name__ == '__main__':
    import unittest
    unittest.main()

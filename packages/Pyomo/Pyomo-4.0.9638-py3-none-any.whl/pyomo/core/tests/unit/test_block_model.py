#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________
#
# Unit Tests for Elements of a Model
#
# TestSimpleCon                Class for testing single constraint
# TestArrayCon                Class for testing array of constraint
#

import logging
import os
import sys

from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

from pyomo.environ import *
from pyomo.opt import *
from pyomo.core.base.connector import ConnectorExpander
import pyutilib.th as unittest
import pyutilib.services


class Test(unittest.TestCase):

    def test_nonindexed_block_immutable_param(self):
        model = AbstractModel()
        def _b_rule(b):
            b.A = Param(initialize=2.0)
        model.B = Block(rule=_b_rule)

        instance = model.create()

        self.assertEqual(value(instance.B.A), 2.0)

    def test_nonindexed_block_mutable_param(self):
        model = AbstractModel()
        def _b_rule(b):
            b.A = Param(initialize=2.0, mutable=True)
        model.B = Block(rule=_b_rule)

        instance = model.create()
        self.assertEqual(value(instance.B.A), 2.0)

        instance.B.A = 4.0
        instance.preprocess()
        self.assertEqual(value(instance.B.A), 4.0)


    def test_indexed_block_immutable_param(self):
        model = AbstractModel()
        model.A = RangeSet(2)
        def _b_rule(b,id):
            b.A = Param(initialize=id)
        model.B = Block(model.A, rule=_b_rule)

        instance = model.create()

        self.assertEqual(value(instance.B[1].A),1)
        self.assertEqual(value(instance.B[2].A),2)

    def test_indexed_block_mutable_param(self):
        model = AbstractModel()
        model.A = RangeSet(2)
        def _b_rule(b,id):
            b.A = Param(initialize=id, mutable=True)
        model.B = Block(model.A, rule=_b_rule)

        instance = model.create()

        self.assertEqual(value(instance.B[1].A),1)
        self.assertEqual(value(instance.B[2].A),2)

        instance.B[1].A = 4.0
        instance.preprocess()
        self.assertEqual(value(instance.B[1].A),4.0)


    def test_create_from_dict(self):
        model = AbstractModel()
        model.A = RangeSet(2)
        def _b_rule(b,id):
            b.S = Set()
            b.P = Param()
            b.Q = Param(b.S)
        model.B = Block(model.A, rule=_b_rule)

        instance = model.create( {None:{'B': \
                                           {1:{'S':{None:['a','b','c']}, \
                                               'P':{None:4}, \
                                               'Q':{('a',):1,('b',):2,('c',):3}}, \
                                            2:{'S':{None:[]}, \
                                               'P':{None:3}} \
                                           } \
                                        }} ) 

        self.assertEqual(set(instance.B[1].S),set(['a','b','c']))
        self.assertEqual(value(instance.B[1].P),4)
        self.assertEqual(value(instance.B[1].Q['a']),1)
        self.assertEqual(value(instance.B[1].Q['b']),2)
        self.assertEqual(value(instance.B[1].Q['c']),3)
        self.assertEqual(value(instance.B[2].P),3)

    def test_expand_connector(self):
        model = AbstractModel()
        model.A = Set()
        def _b_rule(b,id):
            b.X = Var()
            b.PORT = Connector()
            b.PORT.add( b.X )
        model.B = Block(model.A, rule=_b_rule)

        def _c_rule(m,a):
            return m.B[a].PORT == m.B[(a+1)%2].PORT
        model.C = Constraint(model.A,rule=_c_rule)

        instance = model.create( {None: {'A':{None:[0,1]}}} )

        # FIXME: Not sure what to assert here, but at the moment this throws an error anyways. 

    def test_len(self):

        model = AbstractModel()
        model.b = Block()

        # TODO: I think the correct answer should be zero before
        # construction
        self.assertEqual(len(model.b), 1)
        inst = model.create()
        self.assertEqual(len(inst.b), 1)

    def test_none_key(self):

        model = AbstractModel()
        model.b = Block()

        inst = model.create()
        self.assertEqual(id(inst.b), id(inst.b[None]))


if __name__ == "__main__":
    unittest.main()


#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________
#
# Unit Tests for Elements of a Block
#

import os
import sys
import six
from os.path import abspath, dirname, join

currdir = dirname( abspath(__file__) )

import pyutilib.th as unittest
import pyutilib.services
from pyomo.environ import *
from pyomo.core.base.block import SimpleBlock
from pyomo.opt import *

solver = load_solvers('glpk')

class DerivedBlock(SimpleBlock):
    def __init__(self, *args, **kwargs):
        """Constructor"""
        kwargs['ctype'] = DerivedBlock
        super(DerivedBlock, self).__init__(*args, **kwargs)


class TestGenerators(unittest.TestCase):
    
    @ unittest.nottest
    def generate_model(self):
        #
        # ** DO NOT modify the model below without updating the
        # component_lists and component_data_lists with the correct
        # declaration orders
        #

        model = ConcreteModel()
        model.q = Set(initialize=[1,2])
        model.Q = Set(model.q,initialize=[1,2])
        model.x = Var(initialize=-1)
        model.X = Var(model.q,initialize=-1)
        model.e = Expression(initialize=-1)
        model.E = Expression(model.q,initialize=-1)
        model.p = Param(mutable=True,initialize=-1)
        model.P = Param(model.q,mutable=True,initialize=-1)
        model.o = Objective(expr=-1)
        model.O = Objective(model.q, rule=lambda model,i: -1)
        model.c = Constraint(expr=model.x>=-1)
        model.C = Constraint(model.q, rule=lambda model,i: model.X[i]>=-1)
        model.sos = SOSConstraint(var=model.X, set=model.q, sos=1)
        model.SOS = SOSConstraint(model.q, var=model.X, set=model.Q, sos=1)
        model.s = Suffix()

        
        model.b = Block()
        model.b.q = Set(initialize=[1,2])
        model.b.Q = Set(model.b.q,initialize=[1,2])
        model.b.x = Var(initialize=0)
        model.b.X = Var(model.b.q,initialize=0)
        model.b.e = Expression(initialize=0)
        model.b.E = Expression(model.b.q,initialize=0)
        model.b.p = Param(mutable=True,initialize=0)
        model.b.P = Param(model.b.q,mutable=True,initialize=0)
        model.b.o = Objective(expr=0)
        model.b.O = Objective(model.b.q, rule=lambda b,i: 0)
        model.b.c = Constraint(expr=model.b.x>=0)
        model.b.C = Constraint(model.b.q, rule=lambda b,i: b.X[i]>=0)
        model.b.sos = SOSConstraint(var=model.b.X, set=model.b.q, sos=1)
        model.b.SOS = SOSConstraint(model.b.q, var=model.b.X, set=model.b.Q, sos=1)
        model.b.s = Suffix()
        model.b.component_lists = {}
        model.b.component_data_lists = {}
        model.b.component_lists[Set] = [model.b.q, model.b.Q]
        model.b.component_data_lists[Set] = [model.b.q, model.b.Q[1], model.b.Q[2]]
        model.b.component_lists[Var] = [model.b.x, model.b.X]
        model.b.component_data_lists[Var] = [model.b.x, model.b.X[1], model.b.X[2]]
        model.b.component_lists[Expression] = [model.b.e, model.b.E]
        model.b.component_data_lists[Expression] = [model.b.e, model.b.E[1], model.b.E[2]]
        model.b.component_lists[Param] = [model.b.p, model.b.P]
        model.b.component_data_lists[Param] = [model.b.p, model.b.P[1], model.b.P[2]]
        model.b.component_lists[Objective] = [model.b.o, model.b.O]
        model.b.component_data_lists[Objective] = [model.b.o, model.b.O[1], model.b.O[2]]
        model.b.component_lists[Constraint] = [model.b.c, model.b.C]
        model.b.component_data_lists[Constraint] = [model.b.c, model.b.C[1], model.b.C[2]]
        model.b.component_lists[SOSConstraint] = [model.b.sos, model.b.SOS]
        model.b.component_data_lists[SOSConstraint] = [model.b.sos, model.b.SOS[1], model.b.SOS[2]]
        model.b.component_lists[Suffix] = [model.b.s]
        model.b.component_data_lists[Suffix] = [model.b.s]
        model.b.component_lists[Block] = []
        model.b.component_data_lists[Block] = []

        def B_rule(block,i):
            block.q = Set(initialize=[1,2])
            block.Q = Set(block.q,initialize=[1,2])
            block.x = Var(initialize=i)
            block.X = Var(block.q,initialize=i)
            block.e = Expression(initialize=i)
            block.E = Expression(block.q,initialize=i)
            block.p = Param(mutable=True,initialize=i)
            block.P = Param(block.q,mutable=True,initialize=i)
            block.o = Objective(expr=i)
            block.O = Objective(block.q, rule=lambda b,i: i)
            block.c = Constraint(expr=block.x>=i)
            block.C = Constraint(block.q, rule=lambda b,i: b.X[i]>=i)
            block.sos = SOSConstraint(var=block.X, set=block.q, sos=1)
            block.SOS = SOSConstraint(block.q, var=block.X, set=block.Q, sos=1)
            block.s = Suffix()
            block.component_lists = {}
            block.component_data_lists = {}
            block.component_lists[Set] = [block.q, block.Q]
            block.component_data_lists[Set] = [block.q, block.Q[1], block.Q[2]]
            block.component_lists[Var] = [block.x, block.X]
            block.component_data_lists[Var] = [block.x, block.X[1], block.X[2]]
            block.component_lists[Expression] = [block.e, block.E]
            block.component_data_lists[Expression] = [block.e, block.E[1], block.E[2]]
            block.component_lists[Param] = [block.p, block.P]
            block.component_data_lists[Param] = [block.p, block.P[1], block.P[2]]
            block.component_lists[Objective] = [block.o, block.O]
            block.component_data_lists[Objective] = [block.o, block.O[1], block.O[2]]
            block.component_lists[Constraint] = [block.c, block.C]
            block.component_data_lists[Constraint] = [block.c, block.C[1], block.C[2]]
            block.component_lists[SOSConstraint] = [block.sos, block.SOS]
            block.component_data_lists[SOSConstraint] = [block.sos, block.SOS[1], block.SOS[2]]
            block.component_lists[Suffix] = [block.s]
            block.component_data_lists[Suffix] = [block.s]
            block.component_lists[Block] = []
            block.component_data_lists[Block] = []
        model.B = Block(model.q,rule=B_rule)
        
        model.component_lists = {}
        model.component_data_lists = {}
        model.component_lists[Set] = [model.q, model.Q]
        model.component_data_lists[Set] = [model.q, model.Q[1], model.Q[2]]
        model.component_lists[Var] = [model.x, model.X]
        model.component_data_lists[Var] = [model.x, model.X[1], model.X[2]]
        model.component_lists[Expression] = [model.e, model.E]
        model.component_data_lists[Expression] = [model.e, model.E[1], model.E[2]]
        model.component_lists[Param] = [model.p, model.P]
        model.component_data_lists[Param] = [model.p, model.P[1], model.P[2]]
        model.component_lists[Objective] = [model.o, model.O]
        model.component_data_lists[Objective] = [model.o, model.O[1], model.O[2]]
        model.component_lists[Constraint] = [model.c, model.C]
        model.component_data_lists[Constraint] = [model.c, model.C[1], model.C[2]]
        model.component_lists[SOSConstraint] = [model.sos, model.SOS]
        model.component_data_lists[SOSConstraint] = [model.sos, model.SOS[1], model.SOS[2]]
        model.component_lists[Suffix] = [model.s]
        model.component_data_lists[Suffix] = [model.s]
        model.component_lists[Block] = [model.b, model.B]
        model.component_data_lists[Block] = [model.b, model.B[1], model.B[2]]
        
        return model

    @unittest.nottest
    def generator_test(self, ctype):

        model = self.generate_model()

        for block in model.all_blocks(sort=SortComponents.indices):

            # Non-nested active_components
            generator = None
            try:
                generator = list(active_components(block, ctype))
            except:
                if issubclass(ctype, Component):
                    self.fail("active_components failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("active_components should have failed with ctype %s" % ctype)
                # This first check is less safe but it gives a cleaner
                # failure message. I leave comparison of ids in the
                # second assertEqual to make sure the tests are working
                # as expected
                self.assertEqual([comp.cname(True) for comp in generator],
                                 [comp.cname(True) for comp in block.component_lists[ctype]])
                self.assertEqual([id(comp) for comp in generator],
                                 [id(comp) for comp in block.component_lists[ctype]])

            # Non-nested components
            generator = None
            try:
                generator = list(components(block, ctype))
            except:
                if issubclass(ctype, Component):
                    self.fail("components failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("components should have failed with ctype %s" % ctype)
                # This first check is less safe but it gives a cleaner
                # failure message. I leave comparison of ids in the
                # second assertEqual to make sure the tests are working
                # as expected
                self.assertEqual([comp.cname(True) for comp in generator],
                                 [comp.cname(True) for comp in block.component_lists[ctype]])
                self.assertEqual([id(comp) for comp in generator],
                                 [id(comp) for comp in block.component_lists[ctype]])

            # Non-nested active_components_data, sort_by_keys=True
            generator = None
            try:
                generator = list(active_components_data(block, ctype, sort_by_keys=True))
            except:
                if issubclass(ctype, Component):
                    self.fail("active_components_data(sort_by_keys=True) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("active_components_data(sort_by_keys=True) should have failed with ctype %s" % ctype)
                # This first check is less safe but it gives a cleaner
                # failure message. I leave comparison of ids in the
                # second assertEqual to make sure the tests are working
                # as expected
                self.assertEqual([comp.cname(True) for comp in generator],
                                 [comp.cname(True) for comp in block.component_data_lists[ctype]])
                self.assertEqual([id(comp) for comp in generator],
                                 [id(comp) for comp in block.component_data_lists[ctype]])

            # Non-nested active_components_data, sort_by_keys=False
            generator = None
            try:
                generator = list(active_components_data(block, ctype, sort_by_keys=False))
            except:
                if issubclass(ctype, Component):
                    self.fail("active_components_data(sort_by_keys=False) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("active_components_data(sort_by_keys=False) should have failed with ctype %s" % ctype)
                # This first check is less safe but it gives a cleaner
                # failure message. I leave comparison of ids in the
                # second assertEqual to make sure the tests are working
                # as expected
                self.assertEqual(sorted([comp.cname(True) for comp in generator]),
                                 sorted([comp.cname(True) for comp in block.component_data_lists[ctype]]))
                self.assertEqual(sorted([id(comp) for comp in generator]),
                                 sorted([id(comp) for comp in block.component_data_lists[ctype]]))

            # Non-nested components_data, sort_by_keys=True
            generator = None
            try:
                generator = list(components_data(block, ctype, sort_by_keys=True))
            except:
                if issubclass(ctype, Component):
                    self.fail("components_data(sort_by_keys=True) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("components_data(sort_by_keys=True) should have failed with ctype %s" % ctype)
                # This first check is less safe but it gives a cleaner
                # failure message. I leave comparison of ids in the
                # second assertEqual to make sure the tests are working
                # as expected
                self.assertEqual([comp.cname(True) for comp in generator],
                                 [comp.cname(True) for comp in block.component_data_lists[ctype]])
                self.assertEqual([id(comp) for comp in generator],
                                 [id(comp) for comp in block.component_data_lists[ctype]])

            # Non-nested components_data, sort_by_keys=False
            generator = None
            try:
                generator = list(components_data(block, ctype, sort_by_keys=False))
            except:
                if issubclass(ctype, Component):
                    self.fail("components_data(sort_by_keys=False) failed with ctype %s" % ctype)
            else:
                if not issubclass(ctype, Component):
                    self.fail("components_data(sort_by_keys=False) should have failed with ctype %s" % ctype)
                # This first check is less safe but it gives a cleaner
                # failure message. I leave comparison of ids in the
                # second assertEqual to make sure the tests are working
                # as expected
                self.assertEqual(sorted([comp.cname(True) for comp in generator]),
                                 sorted([comp.cname(True) for comp in block.component_data_lists[ctype]]))
                self.assertEqual(sorted([id(comp) for comp in generator]),
                                 sorted([id(comp) for comp in block.component_data_lists[ctype]]))

    def test_Objective(self):
        self.generator_test(Objective)

    def test_Expression(self):
        self.generator_test(Expression)

    def test_Suffix(self):
        self.generator_test(Suffix)

    def test_Constraint(self):
        self.generator_test(Constraint)

    def test_Param(self):
        self.generator_test(Param)

    def test_Var(self):
        self.generator_test(Var)

    def test_Set(self):
        self.generator_test(Set)

    def test_SOSConstraint(self):
        self.generator_test(SOSConstraint)

    def test_Block(self):

        self.generator_test(Block)

        model = self.generate_model()

        # sorted all_blocks
        self.assertEqual([id(comp) for comp in model.all_blocks(sort=SortComponents.deterministic)],
                         [id(comp) for comp in [model,]+model.component_data_lists[Block]])

        # unsorted all_blocks
        self.assertEqual(sorted([id(comp) for comp in model.all_blocks(sort=False)]),
                         sorted([id(comp) for comp in [model,]+model.component_data_lists[Block]]))


class HierarchicalModel(object):
    def __init__(self):
        m = self.model = ConcreteModel()
        m.a1_IDX = Set(initialize=[5,4], ordered=True)
        m.a3_IDX = Set(initialize=[6,7], ordered=True)

        m.c = Block()
        def x(b, i):
            pass
        def a(b, i):
            if i == 1:
                b.d = Block()
                b.c = Block(b.model().a1_IDX, rule=x)
            elif i == 3:
                b.e = Block()
                b.f = Block(b.model().a3_IDX, rule=x)
        m.a = Block([1,2,3], rule=a)
        m.b = Block()

        self.PrefixDFS = [ 
            'unknown', 
            'c', 
            'a[1]', 'a[1].d', 'a[1].c[5]', 'a[1].c[4]', 
            'a[2]', 
            'a[3]', 'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
            'b',
        ]

        self.PrefixDFS_sortIdx = [ 
            'unknown', 
            'c', 
            'a[1]', 'a[1].d', 'a[1].c[4]', 'a[1].c[5]', 
            'a[2]', 
            'a[3]', 'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
            'b',
        ]
        self.PrefixDFS_sortName = [ 
            'unknown', 
            'a[1]', 'a[1].c[5]', 'a[1].c[4]', 'a[1].d', 
            'a[2]', 
            'a[3]', 'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
            'b',
            'c', 
        ]
        self.PrefixDFS_sort = [ 
            'unknown', 
            'a[1]', 'a[1].c[4]', 'a[1].c[5]', 'a[1].d', 
            'a[2]', 
            'a[3]', 'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
            'b',
            'c', 
        ]


        self.PostfixDFS = [ 
            'c', 
            'a[1].d', 'a[1].c[5]', 'a[1].c[4]', 'a[1]', 
            'a[2]', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]', 'a[3]', 
            'b',
            'unknown',
        ]

        self.PostfixDFS_sortIdx = [ 
            'c', 
            'a[1].d', 'a[1].c[4]', 'a[1].c[5]', 'a[1]', 
            'a[2]', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]', 'a[3]', 
            'b',
            'unknown',
        ]
        self.PostfixDFS_sortName = [ 
            'a[1].c[5]', 'a[1].c[4]', 'a[1].d', 'a[1]', 
            'a[2]', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]', 'a[3]', 
            'b',
            'c', 
            'unknown',
        ]
        self.PostfixDFS_sort = [ 
            'a[1].c[4]', 'a[1].c[5]', 'a[1].d', 'a[1]', 
            'a[2]', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]', 'a[3]', 
            'b',
            'c', 
            'unknown',
        ]

        self.BFS = [ 
            'unknown', 
            'c', 
            'a[1]', 'a[2]', 'a[3]', 
            'b',
            'a[1].d', 'a[1].c[5]', 'a[1].c[4]', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
        ]

        self.BFS_sortIdx = [ 
            'unknown', 
            'c', 
            'a[1]', 'a[2]', 'a[3]', 
            'b',
            'a[1].d', 'a[1].c[4]', 'a[1].c[5]', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
        ]
        self.BFS_sortName = [ 
            'unknown', 
            'a[1]', 'a[2]', 'a[3]', 
            'b',
            'c', 
            'a[1].c[5]', 'a[1].c[4]', 'a[1].d', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
        ]
        self.BFS_sort = [ 
            'unknown', 
            'a[1]', 'a[2]', 'a[3]', 
            'b',
            'c', 
            'a[1].c[4]', 'a[1].c[5]', 'a[1].d', 
            'a[3].e', 'a[3].f[6]', 'a[3].f[7]',
        ]

class MixedHierarchicalModel(object):
    def __init__(self):
        m = self.model = ConcreteModel()
        m.a = Block()
        m.a.c = DerivedBlock()
        m.b = DerivedBlock()
        m.b.d = DerivedBlock()
        m.b.e = Block()
        m.b.e.f = DerivedBlock()

        self.PrefixDFS_block = [ 
            'unknown', 
            'a', 
        ]
        self.PostfixDFS_block = [ 
            'a', 
            'unknown', 
        ]
        self.BFS_block = [ 
            'unknown', 
            'a', 
        ]

        self.PrefixDFS_both = [ 
            'unknown', 
            'a', 'a.c',
            'b', 'b.d', 'b.e', 'b.e.f',
        ]
        self.PostfixDFS_both = [ 
            'a.c', 'a',
            'b.d', 'b.e.f', 'b.e', 'b',
            'unknown', 
        ]
        self.BFS_both = [ 
            'unknown', 
            'a', 'b',
            'a.c', 'b.d', 'b.e', 'b.e.f',
        ]


        


        
class TestBlock(unittest.TestCase):

    def setUp(self):
        #
        # Create block
        #
        self.block = Block()
        self.block.construct()

    def tearDown(self):
        if os.path.exists("unknown.lp"):
            os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_clear_attribute(self):
        """ Coverage of the _clear_attribute method """
        obj = Set()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Var()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Param()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Objective()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Constraint()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

        obj = Set()
        self.block.A = obj
        self.assertEqual(self.block.A.name,"A")
        self.assertEqual(obj.name,"A")
        self.assertIs(obj, self.block.A)

    def test_set_attr(self):
        p = Param(mutable=True)
        self.block.x = p
        self.block.x = 5
        self.assertEqual(value(self.block.x), 5)
        self.assertEqual(value(p), 5)
        self.block.x = 6
        self.assertEqual(value(self.block.x), 6)
        self.assertEqual(value(p), 6)
        try:
            self.block.x = None
            self.fail("Expected exception assigning None to domain Any")
        except ValueError:
            pass


    def test_iterate_hierarchy_defaults(self):
        self.assertIs( TraversalStrategy.BFS, 
                       TraversalStrategy.BreadthFirstSearch )

        self.assertIs( TraversalStrategy.DFS, 
                       TraversalStrategy.PrefixDepthFirstSearch )
        self.assertIs( TraversalStrategy.DFS, 
                       TraversalStrategy.PrefixDFS )
        self.assertIs( TraversalStrategy.DFS, 
                       TraversalStrategy.ParentFirstDepthFirstSearch )

        self.assertIs( TraversalStrategy.PostfixDepthFirstSearch, 
                       TraversalStrategy.PostfixDFS )
        self.assertIs( TraversalStrategy.PostfixDepthFirstSearch, 
                       TraversalStrategy.ParentLastDepthFirstSearch )

        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator()]
        self.assertEqual(HM.PrefixDFS, result)

    def test_iterate_hierarchy_PrefixDFS(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PrefixDepthFirstSearch)]
        self.assertEqual(HM.PrefixDFS, result)

    def test_iterate_hierarchy_PrefixDFS_sortIndex(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PrefixDepthFirstSearch,
            sort=SortComponents.indices,
        )]
        self.assertEqual(HM.PrefixDFS_sortIdx, result)
    def test_iterate_hierarchy_PrefixDFS_sortName(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PrefixDepthFirstSearch,
            sort=SortComponents.alphaOrder,
        )]
        self.assertEqual(HM.PrefixDFS_sortName, result)
    def test_iterate_hierarchy_PrefixDFS_sort(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PrefixDepthFirstSearch,
            sort=True
        )]
        self.assertEqual(HM.PrefixDFS_sort, result)


    def test_iterate_hierarchy_PostfixDFS(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PostfixDepthFirstSearch)]
        self.assertEqual(HM.PostfixDFS, result)

    def test_iterate_hierarchy_PostfixDFS_sortIndex(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PostfixDepthFirstSearch,
            sort=SortComponents.indices,
        )]
        self.assertEqual(HM.PostfixDFS_sortIdx, result)
    def test_iterate_hierarchy_PostfixDFS_sortName(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PostfixDepthFirstSearch,
            sort=SortComponents.alphaOrder,
        )]
        self.assertEqual(HM.PostfixDFS_sortName, result)
    def test_iterate_hierarchy_PostfixDFS_sort(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PostfixDepthFirstSearch,
            sort=True
        )]
        self.assertEqual(HM.PostfixDFS_sort, result)

    def test_iterate_hierarchy_BFS(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.BreadthFirstSearch)]
        self.assertEqual(HM.BFS, result)


    def test_iterate_hierarchy_BFS_sortIndex(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.BreadthFirstSearch,
            sort=SortComponents.indices,
        )]
        self.assertEqual(HM.BFS_sortIdx, result)
    def test_iterate_hierarchy_BFS_sortName(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.BreadthFirstSearch,
            sort=SortComponents.alphaOrder,
        )]
        self.assertEqual(HM.BFS_sortName, result)
    def test_iterate_hierarchy_BFS_sort(self):
        HM = HierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.BreadthFirstSearch,
            sort=True
        )]
        self.assertEqual(HM.BFS_sort, result)

    def test_iterate_mixed_hierarchy_PrefixDFS_block(self):
        HM = MixedHierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PrefixDepthFirstSearch,
            ctype=Block,
        )]
        self.assertEqual(HM.PrefixDFS_block, result)
    def test_iterate_mixed_hierarchy_PrefixDFS_both(self):
        HM = MixedHierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PrefixDepthFirstSearch,
            ctype=(Block,DerivedBlock), 
        )]
        self.assertEqual(HM.PrefixDFS_both, result)

    def test_iterate_mixed_hierarchy_PostfixDFS_block(self):
        HM = MixedHierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PostfixDepthFirstSearch,
            ctype=Block,
        )]
        self.assertEqual(HM.PostfixDFS_block, result)
    def test_iterate_mixed_hierarchy_PostfixDFS_both(self):
        HM = MixedHierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.PostfixDepthFirstSearch,
            ctype=(Block,DerivedBlock), 
        )]
        self.assertEqual(HM.PostfixDFS_both, result)

    def test_iterate_mixed_hierarchy_BFS_block(self):
        HM = MixedHierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.BFS,
            ctype=Block,
        )]
        self.assertEqual(HM.BFS_block, result)
    def test_iterate_mixed_hierarchy_BFS_both(self):
        HM = MixedHierarchicalModel()
        m = HM.model
        result = [x.cname(True) for x in m.tree_iterator(
            traversal=TraversalStrategy.BFS,
            ctype=(Block,DerivedBlock), 
        )]
        self.assertEqual(HM.BFS_both, result)


    def test_add_remove_component_byname(self):
        m = Block()
        self.assertFalse(m.contains_component(Var))
        self.assertFalse(m.components(Var))

        m.x = x = Var()
        self.assertTrue(m.contains_component(Var))
        self.assertTrue(m.components(Var))
        self.assertTrue('x' in m.__dict__)
        self.assertIs(m.component('x'), x)

        m.del_component('x')
        self.assertFalse(m.contains_component(Var))
        self.assertFalse(m.components(Var))
        self.assertFalse('x' in m.__dict__)
        self.assertIs(m.component('x'), None)
        
    def test_add_remove_component_byref(self):
        m = Block()
        self.assertFalse(m.contains_component(Var))
        self.assertFalse(m.components(Var))

        m.x = x = Var()
        self.assertTrue(m.contains_component(Var))
        self.assertTrue(m.components(Var))
        self.assertTrue('x' in m.__dict__)
        self.assertIs(m.component('x'), x)

        m.del_component(m.x)
        self.assertFalse(m.contains_component(Var))
        self.assertFalse(m.components(Var))
        self.assertFalse('x' in m.__dict__)
        self.assertIs(m.component('x'), None)
        
    def test_add_del_component(self):
        m = Block()
        self.assertFalse(m.contains_component(Var))
        m.x = x = Var()
        self.assertTrue(m.contains_component(Var))
        self.assertTrue('x' in m.__dict__)
        self.assertIs(m.component('x'), x)
        del m.x
        self.assertFalse(m.contains_component(Var))
        self.assertFalse('x' in m.__dict__)
        self.assertIs(m.component('x'), None)
    
    def test_reclassify_component(self):
        m = Block()
        m.a = Var()
        m.b = Var()
        m.c = Param()

        self.assertEqual(len(m.components(Var)), 2)
        self.assertEqual(len(m.components(Param)), 1)
        self.assertEqual( ['a', 'b'], list(m.components(Var)) )
        self.assertEqual( ['c'], list(m.components(Param)) )

        # Test removing from the end of a list and appending to the beginning
        # of a list
        m.reclassify_component_type(m.b, Param)
        self.assertEqual(len(m.components(Var)), 1)
        self.assertEqual(len(m.components(Param)), 2)
        self.assertEqual( ['a'], list(m.components(Var)) )
        self.assertEqual( ['b','c'], list(m.components(Param)) )

        # Test removing from the beginning of a list and appending to
        # the end of a list
        m.reclassify_component_type(m.b, Var)
        self.assertEqual(len(m.components(Var)), 2)
        self.assertEqual(len(m.components(Param)), 1)
        self.assertEqual( ['a','b'], list(m.components(Var)) )
        self.assertEqual( ['c'], list(m.components(Param)) )

        # Test removing the last element of a list and creating a new list
        m.reclassify_component_type(m.c, Var)
        self.assertEqual(len(m.components(Var)), 3)
        self.assertEqual(len(m.components(Param)), 0)
        self.assertTrue(m.contains_component(Var))
        self.assertFalse(m.contains_component(Param))
        self.assertFalse(m.contains_component(Constraint))
        self.assertEqual( ['a','b','c'], list(m.components(Var)) )
        self.assertEqual( [], list(m.components(Param)) )

        # Test removing the last element of a list and creating a new list
        m.reclassify_component_type(m.c, Param)
        self.assertEqual(len(m.components(Var)), 2)
        self.assertEqual(len(m.components(Param)), 1)
        self.assertEqual(len(m.components(Constraint)), 0)
        self.assertTrue(m.contains_component(Var))
        self.assertTrue(m.contains_component(Param))
        self.assertFalse(m.contains_component(Constraint))
        self.assertEqual( ['a','b'], list(m.components(Var)) )
        self.assertEqual( ['c'], list(m.components(Param)) )

        # Test removing the first element of a list and creating a new list
        m.reclassify_component_type(m.a, Constraint)
        self.assertEqual(len(m.components(Var)), 1)
        self.assertEqual(len(m.components(Param)), 1)
        self.assertEqual(len(m.components(Constraint)), 1)
        self.assertTrue(m.contains_component(Var))
        self.assertTrue(m.contains_component(Param))
        self.assertTrue(m.contains_component(Constraint))
        self.assertEqual( ['b'], list(m.components(Var)) )
        self.assertEqual( ['c'], list(m.components(Param)) )
        self.assertEqual( ['a'], list(m.components(Constraint)) )

        # Test removing the last element of a list and inserting it into
        # the middle of new list
        m.reclassify_component_type(m.a, Param)
        m.reclassify_component_type(m.b, Param)
        self.assertEqual(len(m.components(Var)), 0)
        self.assertEqual(len(m.components(Param)), 3)
        self.assertEqual(len(m.components(Constraint)), 0)
        self.assertFalse(m.contains_component(Var))
        self.assertTrue(m.contains_component(Param))
        self.assertFalse(m.contains_component(Constraint))
        self.assertEqual( [], list(m.components(Var)) )
        self.assertEqual( ['a','b','c'], list(m.components(Param)) )
        self.assertEqual( [], list(m.components(Constraint)) )

        # Test idnoring decl order
        m.reclassify_component_type( 'b', Var, 
                                        preserve_declaration_order=False )
        m.reclassify_component_type( 'c', Var,
                                        preserve_declaration_order=False )
        m.reclassify_component_type( 'a', Var,
                                        preserve_declaration_order=False )
        self.assertEqual(len(m.components(Var)), 3)
        self.assertEqual(len(m.components(Param)), 0)
        self.assertEqual(len(m.components(Constraint)), 0)
        self.assertTrue(m.contains_component(Var))
        self.assertFalse(m.contains_component(Param))
        self.assertFalse(m.contains_component(Constraint))
        self.assertEqual( ['b','c','a'], list(m.components(Var)) )
        self.assertEqual( [], list(m.components(Param)) )
        self.assertEqual( [], list(m.components(Constraint)) )

    def test_pseudomap_len(self):
        m = Block()
        m.a = Var()
        m.b = Var() # active=False
        m.c = Var()
        m.z = Param() # active=False
        m.x = Param()
        m.v = Param()
        m.y = Param()
        m.w = Param() # active=False
        
        m.b.deactivate()
        m.z.deactivate()
        m.w.deactivate()

        self.assertEqual(len(m.components()), 8)
        self.assertEqual(len(m.components(active=True)), 5)
        self.assertEqual(len(m.components(active=False)), 3)

        self.assertEqual(len(m.components(Var)), 3)
        self.assertEqual(len(m.components(Var, active=True)), 2)
        self.assertEqual(len(m.components(Var, active=False)), 1)

        self.assertEqual(len(m.components(Param)), 5)
        self.assertEqual(len(m.components(Param, active=True)), 3)
        self.assertEqual(len(m.components(Param, active=False)), 2)

    def test_pseudomap_contains(self):
        m = Block()
        m.a = Var()
        m.b = Var() # active=False
        m.c = Var()
        m.s = Set()
        m.t = Suffix()
        m.z = Param() # active=False
        m.x = Param()
        m.b.deactivate()
        m.z.deactivate()

        pm = m.components()
        self.assertTrue('a' in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' in pm)
        self.assertTrue('t' in pm)
        self.assertTrue('x' in pm)
        self.assertTrue('z' in pm)

        pm = m.components(active=True)
        self.assertTrue('a' in pm)
        self.assertTrue('b' not in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' in pm)
        self.assertTrue('t' in pm)
        self.assertTrue('x' in pm)
        self.assertTrue('z' not in pm)

        pm = m.components(active=False)
        self.assertTrue('a' not in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' not in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' not in pm)
        self.assertTrue('t' not in pm)
        self.assertTrue('x' not in pm)
        self.assertTrue('z' in pm)


        pm = m.components(Var)
        self.assertTrue('a' in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('x' not in pm)
        self.assertTrue('z' not in pm)

        pm = m.components(Var, active=True)
        self.assertTrue('a' in pm)
        self.assertTrue('b' not in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('x' not in pm)
        self.assertTrue('z' not in pm)

        pm = m.components(Var, active=False)
        self.assertTrue('a' not in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' not in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('x' not in pm)
        self.assertTrue('z' not in pm)


        pm = m.components([Var,Param])
        self.assertTrue('a' in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' not in pm)
        self.assertTrue('t' not in pm)
        self.assertTrue('x' in pm)
        self.assertTrue('z' in pm)

        pm = m.components([Var,Param], active=True)
        self.assertTrue('a' in pm)
        self.assertTrue('b' not in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' not in pm)
        self.assertTrue('t' not in pm)
        self.assertTrue('x' in pm)
        self.assertTrue('z' not in pm)

        pm = m.components([Var,Param], active=False)
        self.assertTrue('a' not in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' not in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' not in pm)
        self.assertTrue('t' not in pm)
        self.assertTrue('x' not in pm)
        self.assertTrue('z' in pm)


        # You should be able to pass in a set as well as a list
        pm = m.components(set([Var,Param]))
        self.assertTrue('a' in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' not in pm)
        self.assertTrue('t' not in pm)
        self.assertTrue('x' in pm)
        self.assertTrue('z' in pm)

        pm = m.components(set([Var,Param]), active=True)
        self.assertTrue('a' in pm)
        self.assertTrue('b' not in pm)
        self.assertTrue('c' in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' not in pm)
        self.assertTrue('t' not in pm)
        self.assertTrue('x' in pm)
        self.assertTrue('z' not in pm)

        pm = m.components(set([Var,Param]), active=False)
        self.assertTrue('a' not in pm)
        self.assertTrue('b' in pm)
        self.assertTrue('c' not in pm)
        self.assertTrue('d' not in pm)
        self.assertTrue('s' not in pm)
        self.assertTrue('t' not in pm)
        self.assertTrue('x' not in pm)
        self.assertTrue('z' in pm)


    def test_pseudomap_getitem(self):
        m = Block()
        m.a = a = Var()
        m.b = b = Var() # active=False
        m.c = c = Var()
        m.s = s = Set()
        m.t = t = Suffix()
        m.z = z = Param() # active=False
        m.x = x = Param()
        m.b.deactivate()
        m.z.deactivate()

        def assertWorks(self, key, pm):
            self.assertIs(pm[key.cname()], key)
        def assertFails(self, key, pm):
            if not isinstance(key, six.string_types):
                key = key.cname()
            self.assertRaises(KeyError, pm.__getitem__, key)

        pm = m.components()
        assertWorks(self, a, pm)
        assertWorks(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertWorks(self, s, pm)
        assertWorks(self, t, pm)
        assertWorks(self, x, pm)
        assertWorks(self, z, pm)

        pm = m.components(active=True)
        assertWorks(self, a, pm)
        assertFails(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertWorks(self, s, pm)
        assertWorks(self, t, pm)
        assertWorks(self, x, pm)
        assertFails(self, z, pm)

        pm = m.components(active=False)
        assertFails(self, a, pm)
        assertWorks(self, b, pm)
        assertFails(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertFails(self, x, pm)
        assertWorks(self, z, pm)


        pm = m.components(Var)
        assertWorks(self, a, pm)
        assertWorks(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertFails(self, x, pm)
        assertFails(self, z, pm)

        pm = m.components(Var, active=True)
        assertWorks(self, a, pm)
        assertFails(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertFails(self, x, pm)
        assertFails(self, z, pm)

        pm = m.components(Var, active=False)
        assertFails(self, a, pm)
        assertWorks(self, b, pm)
        assertFails(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertFails(self, x, pm)
        assertFails(self, z, pm)


        pm = m.components([Var,Param])
        assertWorks(self, a, pm)
        assertWorks(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertWorks(self, x, pm)
        assertWorks(self, z, pm)

        pm = m.components([Var,Param], active=True)
        assertWorks(self, a, pm)
        assertFails(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertWorks(self, x, pm)
        assertFails(self, z, pm)

        pm = m.components([Var,Param], active=False)
        assertFails(self, a, pm)
        assertWorks(self, b, pm)
        assertFails(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertFails(self, x, pm)
        assertWorks(self, z, pm)


        pm = m.components(set([Var,Param]))
        assertWorks(self, a, pm)
        assertWorks(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertWorks(self, x, pm)
        assertWorks(self, z, pm)

        pm = m.components(set([Var,Param]), active=True)
        assertWorks(self, a, pm)
        assertFails(self, b, pm)
        assertWorks(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertWorks(self, x, pm)
        assertFails(self, z, pm)

        pm = m.components(set([Var,Param]), active=False)
        assertFails(self, a, pm)
        assertWorks(self, b, pm)
        assertFails(self, c, pm)
        assertFails(self, 'd', pm)
        assertFails(self, s, pm)
        assertFails(self, t, pm)
        assertFails(self, x, pm)
        assertWorks(self, z, pm)

    def test_pseudomap_getitem_exceptionString(self):
        def tester(pm, _str):
            try:
                pm['a']
                self.fail("Expected PseudoMap to raise a KeyError")
            except KeyError:
                err = sys.exc_info()[1].args[0]
                self.assertEqual(_str, err)
        
        m = Block(name='foo')
        tester( m.components(), 
                "component 'a' not found in block foo" )
        tester( m.components(active=True), 
                "active component 'a' not found in block foo" )
        tester( m.components(active=False), 
                "inactive component 'a' not found in block foo" )

        tester( m.components(Var), 
                "Var component 'a' not found in block foo" )
        tester( m.components(Var, active=True), 
                "active Var component 'a' not found in block foo" )
        tester( m.components(Var, active=False), 
                "inactive Var component 'a' not found in block foo" )

        tester( m.components([Var,Param]), 
                "Param or Var component 'a' not found in block foo" )
        tester( m.components(set([Var,Param]), active=True), 
                "active Param or Var component 'a' not found in block foo" )
        tester( m.components(set([Var,Param]), active=False), 
                "inactive Param or Var component 'a' not found in block foo" )


        tester(
            m.components(set([Set,Var,Param])), 
            "Param, Set or Var component 'a' not found in block foo" )
        tester(
            m.components(set([Set,Var,Param]), active=True), 
            "active Param, Set or Var component 'a' not found in block foo" )
        tester( 
            m.components(set([Set,Var,Param]), active=False), 
            "inactive Param, Set or Var component 'a' not found in block foo" )

    def test_pseudomap_iteration(self):
        m = Block()
        m.a = Var()
        m.z = Param() # active=False
        m.x = Param()
        m.v = Param()
        m.b = Var() # active=False
        m.t = Set()
        m.s = Set()
        m.c = Var()
        m.y = Param()
        m.w = Param() # active=False
        
        m.b.deactivate()
        m.z.deactivate()
        m.w.deactivate()
        m.t.deactivate()

        self.assertEqual( ['a','z','x','v','b','t','s','c','y','w'], 
                          list(m.components()) )

        self.assertEqual( ['a','z','x','v','b','c','y','w'], 
                          list(m.components( set([Var,Param]) )) )

        # test that the order of ctypes in the argument does not affect
        # the order in the resulting list
        self.assertEqual( ['a','z','x','v','b','c','y','w'], 
                          list(m.components( [Var,Param] )) )

        self.assertEqual( ['a','z','x','v','b','c','y','w'], 
                          list(m.components( [Param,Var] )) )

        self.assertEqual( ['a','b','c'], 
                          list(m.components( Var )) )

        self.assertEqual( ['z','x','v','y','w'], 
                          list(m.components( set([Param]) )) )
        
        self.assertEqual( ['a','x','v','s','c','y'], 
                          list(m.components( active=True )) )

        self.assertEqual( ['a','x','v','c','y'], 
                          list(m.components( set([Var,Param]), active=True )) )

        self.assertEqual( ['a','x','v','c','y'], 
                          list(m.components( [Var,Param], active=True )) )

        self.assertEqual( ['a','x','v','c','y'], 
                          list(m.components( [Param,Var], active=True )) )

        self.assertEqual( ['a','c'], 
                          list(m.components( Var, active=True )) )

        self.assertEqual( ['x','v','y'], 
                          list(m.components( set([Param]), active=True )) )
        
        self.assertEqual( ['z','b','t','w'], 
                          list(m.components( active=False )) )

        self.assertEqual( ['z','b','w'], 
                          list(m.components( set([Var,Param]), active=False )) )

        self.assertEqual( ['z','b','w'], 
                          list(m.components( [Var,Param], active=False )) )

        self.assertEqual( ['z','b','w'], 
                          list(m.components( [Param,Var], active=False )) )

        self.assertEqual( ['b'], 
                          list(m.components( Var, active=False )) )

        self.assertEqual( ['z','w'], 
                          list(m.components( set([Param]), active=False )) )
        

        self.assertEqual( ['a','b','c','s','t','v','w','x','y','z'], 
                          list(m.components( sort=True )) )

        self.assertEqual( ['a','b','c','v','w','x','y','z'], 
                          list(m.components( set([Var,Param]),sort=True )) )

        self.assertEqual( ['a','b','c','v','w','x','y','z'], 
                          list(m.components( [Var,Param],sort=True )) )

        self.assertEqual( ['a','b','c','v','w','x','y','z'], 
                          list(m.components( [Param,Var],sort=True )) )

        self.assertEqual( ['a','b','c'], 
                          list(m.components( Var,sort=True )) )

        self.assertEqual( ['v','w','x','y','z'], 
                          list(m.components( set([Param]),sort=True )) )
        
        self.assertEqual( ['a','c','s','v','x','y'], 
                          list(m.components( active=True,sort=True )) )

        self.assertEqual( ['a','c','v','x','y'], 
                          list(m.components( set([Var,Param]), active=True,
                                                sort=True )) )

        self.assertEqual( ['a','c','v','x','y'], 
                          list(m.components( [Var,Param], active=True,
                                                sort=True )) )

        self.assertEqual( ['a','c','v','x','y'], 
                          list(m.components( [Param,Var], active=True,
                                                sort=True )) )

        self.assertEqual( ['a','c'], 
                          list(m.components( Var, active=True, sort=True )) )

        self.assertEqual( ['v','x','y'], 
                          list(m.components( set([Param]), active=True,
                                                sort=True )) )
        
        self.assertEqual( ['b','t','w','z'], 
                          list(m.components( active=False, sort=True )) )

        self.assertEqual( ['b','w','z'], 
                          list(m.components( set([Var,Param]), active=False,
                                                sort=True )) )

        self.assertEqual( ['b','w','z'], 
                          list(m.components( [Var,Param], active=False,
                                                sort=True )) )

        self.assertEqual( ['b','w','z'], 
                          list(m.components( [Param,Var], active=False,
                                                sort=True )) )

        self.assertEqual( ['b'], 
                          list(m.components( Var, active=False, 
                                                sort=True )) )

        self.assertEqual( ['w','z'], 
                          list(m.components( set([Param]), active=False, 
                                                sort=True )) )
        


    def Xtest_display(self):
        self.block.A = RangeSet(1,4)
        self.block.x = Var(self.block.A, bounds=(-1,1))
        def obj_rule(block):
            return summation(block.x)
        self.block.obj = Objective(rule=obj_rule)
        #self.instance = self.block.create()
        #self.block.pprint()
        #self.block.display()

    def Xtest_write2(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            return (1, model.x[1]+model.x[2], 2)
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        self.instance.write()

    def Xtest_write3(self):
        """Test that the summation works correctly, even though param 'w' has a default value"""
        self.model.J = RangeSet(1,4)
        self.model.w=Param(self.model.J, default=4)
        self.model.x=Var(self.model.J)
        def obj_rule(instance):
            return summation(instance.x, instance.w)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.assertEqual(len(self.instance.obj[None].expr._args), 4)

    def Xtest_solve1(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        #self.instance.pprint()
        opt = solver['glpk']
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1.txt"))
        #
        def d_rule(model):
            return model.x[1] > 0
        self.model.d = Constraint(rule=d_rule)
        self.model.d.deactivate()
        self.instance = self.model.create()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(currdir+"solve1.out")
        self.assertFileEqualsBaseline(currdir+"solve1.out",currdir+"solve1.txt")
        #
        self.model.d.activate()
        self.instance = self.model.create()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1a.txt"))
        #
        self.model.d.deactivate()
        def e_rule(i, model):
            return model.x[i] > 0
        self.model.e = Constraint(self.model.A, rule=e_rule)
        self.instance = self.model.create()
        for i in self.instance.A:
            self.instance.e[i].deactivate()
        solutions = opt.solve(self.instance, keepfiles=True)
        self.instance.load(solutions)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1b.txt"))

    def Xtest_load1(self):
        """Testing loading of vector solutions"""
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        ans = [0.75]*4
        self.instance.load(ans)
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1c.txt"))

    def Xtest_solve3(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            expr = 0
            for i in model.A:
                expr += model.x[i]
            return expr
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve3.txt"))

    def Xtest_solve4(self):
        self.model.A = RangeSet(1,4)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x)
        self.model.obj = Objective(rule=obj_rule)
        def c_rule(model):
            expr = 0
            for i in model.A:
                expr += i*model.x[i]
            return expr == 0
        self.model.c = Constraint(rule=c_rule)
        self.instance = self.model.create()
        #self.instance.pprint()
        opt = solver['glpk']
        solutions = opt.solve(self.instance)
        self.instance.load(solutions.solution(0))
        self.instance.display(join(currdir,"solve1.out"))
        self.assertFileEqualsBaseline(join(currdir,"solve1.out"),join(currdir,"solve1.txt"))

if __name__ == "__main__":
    unittest.main()

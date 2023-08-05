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
from six import StringIO
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

from pyomo.core.base import IntegerSet
from pyomo.environ import *
from pyomo.opt import *
import pyutilib.th as unittest
import pyutilib.services

class LogBuffer(object):

    def __init__(self, logger, logLevel=None):
        if isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            self.logger = logging.getLogger(logger)
        self.buffer = StringIO()
        if logLevel is None:
            self.old_level = None
        else:
            self.old_level = self.logger.getEffectiveLevel()
            self.logger.setLevel(logLevel)
            
        self.logHandler = logging.StreamHandler(self.buffer)
        self.logger.addHandler(self.logHandler)

    def __del__(self):
        self.close()

    def close(self):
        if self.logger is None:
            return
        if self.old_level is not None:
            self.logger.setLevel(self.old_level)

        self.logger.removeHandler(self.logHandler)
        self.logHandler.flush()
        self.buffer.flush()
        self.logHandler = None
        self.logger = None

    def value(self):
        if self.logHandler is not None:
            self.logHandler.flush();
        self.buffer.flush()
        return self.buffer.getvalue()


class TestConstraintCreation(unittest.TestCase):

    def create_model(self,abstract=False):
        if abstract is True:
            model = AbstractModel()
        else:
            model = ConcreteModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        return model

    def test_tuple_construct_equality(self):
        model = self.create_model()
        def rule(model):
            return (0.0, model.x)
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         True)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.x)
        self.assertEqual(model.c.upper,             0)

        def rule(model):
            return (model.x, 0.0)
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         True)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.x)
        self.assertEqual(model.c.upper,             0)

    def test_tuple_construct_inf_equality(self):
        model = self.create_model(abstract=True)
        def rule(model):
            return (model.x, float('inf'))
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)

        def rule(model):
            return (float('inf'), model.x)
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)


    def test_tuple_construct_1sided_inequality(self):
        model = self.create_model()
        def rule(model):
            return (None, model.y, 1)
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             1)

        def rule(model):
            return (0, model.y, None)
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

    def test_tuple_construct_1sided_inf_inequality(self):
        model = self.create_model()
        def rule(model):
            return (float('-inf'), model.y, 1)
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             1)

        def rule(model):
            return (0, model.y, float('inf'))
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

    def test_tuple_construct_unbounded_inequality(self):
        model = self.create_model()
        def rule(model):
            return (None, model.y, None)
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

        def rule(model):
            return (float('-inf'), model.y, float('inf'))
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

    def test_tuple_construct_invalid_1sided_inequality(self):
        model = self.create_model(abstract=True)
        def rule(model):
            return (model.x, model.y, None)
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)

        def rule(model):
            return (None, model.y, model.z)
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)


    def test_tuple_construct_2sided_inequality(self):
        model = self.create_model()
        def rule(model):
            return (0, model.y, 1)
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             1)

    def test_tuple_construct_invalid_2sided_inequality(self):
        model = self.create_model(abstract=True)
        def rule(model):
            return (model.x, model.y, 1)
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)

        def rule(model):
            return (0, model.y, model.z)
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)



    def test_expr_construct_equality(self):
        model = self.create_model()
        def rule(model):
            return 0.0 == model.x
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         True)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.x)
        self.assertEqual(model.c.upper,             0)

        def rule(model):
            return model.x == 0.0
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         True)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.x)
        self.assertEqual(model.c.upper,             0)

    def test_expr_construct_inf_equality(self):
        model = self.create_model(abstract=True)
        def rule(model):
            return model.x == float('inf')
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)

        def rule(model):
            return float('inf') == model.x
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)


    def test_expr_construct_1sided_inequality(self):
        model = self.create_model()
        def rule(model):
            return model.y <= 1
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             1)

        def rule(model):
            return 0 <= model.y
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             0)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

        def rule(model):
            return model.y >= 1
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             1)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

        def rule(model):
            return 0 >= model.y
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             0)

    def test_expr_construct_unbounded_inequality(self):
        model = self.create_model()
        def rule(model):
            return model.y <= float('inf')
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

        def rule(model):
            return float('-inf') <= model.y
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

        def rule(model):
            return model.y >= float('-inf')
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

        def rule(model):
            return float('inf') >= model.y
        model.c = Constraint(rule=rule)
        
        self.assertEqual(model.c._equality,         False)
        self.assertEqual(model.c.lower,             None)
        self.assertIs   (model.c.body,              model.y)
        self.assertEqual(model.c.upper,             None)

    def test_expr_construct_invalid_unbounded_inequality(self):
        model = self.create_model(abstract=True)
        def rule(model):
            return model.y <= float('-inf')
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)

        def rule(model):
            return float('inf') <= model.y
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)

        def rule(model):
            return model.y >= float('inf')
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)

        def rule(model):
            return float('-inf') >= model.y
        model.c = Constraint(rule=rule)
        self.assertRaises(ValueError, model.create)


class TestSimpleCon(unittest.TestCase):

    def test_set_expr_explicit_multivariate(self):
        """Test expr= option (multivariate expression)"""
        model = ConcreteModel()
        model.x = Var(RangeSet(1,4),initialize=2)
        ans=0
        for i in model.x:
            ans = ans + model.x[i]
        ans = ans >= 0
        ans = ans <= 1
        model.c = Constraint(expr=ans)
        
        self.assertEqual(model.c(), 8)
        self.assertEqual(model.c.body(), 8)
        self.assertEqual(value(model.c.body), 8)

    def test_set_expr_explicit_univariate(self):
        """Test expr= option (univariate expression)"""
        model = ConcreteModel()
        model.x = Var(initialize=2)
        ans = model.x >= 0
        ans = ans <= 1
        model.c = Constraint(expr=ans)
        
        self.assertEqual(model.c(), 2)
        self.assertEqual(model.c.body(), 2)
        self.assertEqual(value(model.c.body), 2)

    def test_set_expr_undefined_univariate(self):
        """Test expr= option (univariate expression)"""
        model = ConcreteModel()
        model.x = Var()
        ans = model.x >= 0
        ans = ans <= 1
        model.c = Constraint(expr=ans)
        
        #self.assertRaises(ValueError, model.c)
        self.assertEqual(model.c(),None)
        model.x = 2
        self.assertEqual(model.c(), 2)
        self.assertEqual(value(model.c.body), 2)

    def test_set_expr_inline(self):
        """Test expr= option (inline expression)"""
        model = ConcreteModel()
        model.A = RangeSet(1,4)
        model.x = Var(model.A,initialize=2)
        model.c = Constraint(expr=0 <= sum(model.x[i] for i in model.A) <= 1)
        
        self.assertEqual(model.c(), 8)
        self.assertEqual(value(model.c.body), 8)

    def test_rule1(self):
        """Test rule option"""
        model = ConcreteModel()
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            ans = ans >= 0
            ans = ans <= 1
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(rule=f)
        
        self.assertEqual(model.c(), 8)
        self.assertEqual(value(model.c.body), 8)

    def test_rule2(self):
        """Test rule option"""
        model = ConcreteModel()
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (0,ans,1)
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(rule=f)
        
        self.assertEqual(model.c(), 8)
        self.assertEqual(value(model.c.body), 8)

    def test_rule3(self):
        """Test rule option"""
        model = ConcreteModel()
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (0,ans,None)
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(rule=f)
        
        self.assertEqual(model.c(), 8)
        self.assertEqual(value(model.c.body), 8)

    def test_rule4(self):
        """Test rule option"""
        model = ConcreteModel()
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (None,ans,1)
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(rule=f)
        
        self.assertEqual(model.c(), 8)
        self.assertEqual(value(model.c.body), 8)

    def test_rule5(self):
        """Test rule option"""
        model = ConcreteModel()
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            return (ans,1)
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(rule=f)
        
        self.assertEqual(model.c(), 8)
        self.assertEqual(value(model.c.body), 8)

    def test_dim(self):
        """Test dim method"""
        model = ConcreteModel()
        model.c = Constraint(noruleinit=True)
        
        self.assertEqual(model.c.dim(),0)

    def test_keys_noruleinit(self):
        """Test keys method"""
        model = ConcreteModel()
        model.c = Constraint(noruleinit=True)
        
        self.assertEqual(list(model.c.keys()),[])

    def test_len_noruleinit(self):
        """Test len method"""
        model = ConcreteModel()
        model.c = Constraint(noruleinit=True)
        
        self.assertEqual(len(model.c),0)

    def test_None_key(self):
        """Test keys method"""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x == 1)
        
        self.assertEqual(list(model.c.keys()),[None])
        self.assertEqual(id(model.c),id(model.c[None]))

    def test_len(self):
        """Test len method"""
        model = AbstractModel()
        model.x = Var()
        model.c = Constraint(rule=lambda m: m.x == 1)
        
        self.assertEqual(len(model.c),0)
        inst = model.create()
        self.assertEqual(len(inst.c),1)


class TestArrayCon(unittest.TestCase):

    def create_model(self):
        model = ConcreteModel()
        model.A = Set(initialize=[1,2,3,4])
        return model

    def test_rule_option1(self):
        """Test rule option"""
        model = self.create_model()
        def f(model, i):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(model.c[2](), 16)
        self.assertEqual(len(model.c), 4)

    def test_old_rule_option1(self):
        """Test rule option"""
        model = self.create_model()
        buffer = LogBuffer('pyomo.core', logging.WARNING)
        def f(model, i):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(model.c[2](), 16)
        self.assertEqual(len(model.c), 4)

    def test_rule_option2(self):
        """Test rule option"""
        model = self.create_model()
        def f(model, i):
            if i%2 == 0:
                return Constraint.Skip
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(len(model.c), 2)

    def test_rule_option3(self):
        """Test rule option"""
        model = self.create_model()
        def f(model, i):
            if i%2 == 0:
                return Constraint.Skip
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(len(model.c), 2)

    def test_rule_option2a(self):
        """Test rule option"""
        model = self.create_model()
        @simple_constraint_rule
        def f(model, i):
            if i%2 == 0:
                return None
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(len(model.c), 2)

    def test_rule_option3a(self):
        """Test rule option"""
        model = self.create_model()
        @simple_constraint_rule
        def f(model, i):
            if i%2 == 0:
                return None
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(len(model.c), 2)

    def test_dim(self):
        """Test dim method"""
        model = self.create_model()
        model.c = Constraint(model.A, noruleinit=True)
        
        self.assertEqual(model.c.dim(),1)

    def test_keys(self):
        """Test keys method"""
        model = self.create_model()
        model.c = Constraint(model.A, noruleinit=True)
        
        self.assertEqual(len(model.c.keys()),0)

    def test_len(self):
        """Test len method"""
        model = self.create_model()
        model.c = Constraint(model.A, noruleinit=True)
        
        self.assertEqual(len(model.c),0)
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            ans = ans==2
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(rule=f)
        
        self.assertEqual(len(model.c),1)


class TestConList(unittest.TestCase):

    def create_model(self):
        model = ConcreteModel()
        model.A = Set(initialize=[1,2,3,4])
        return model

    def test_rule_option1(self):
        """Test rule option"""
        model = self.create_model()
        def f(model, i):
            if i > 4:
                return ConstraintList.End
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = ConstraintList(rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(model.c[2](), 16)
        self.assertEqual(len(model.c), 4)

    def test_rule_option2(self):
        """Test rule option"""
        model = self.create_model()
        def f(model, i):
            if i > 2:
                return ConstraintList.End
            i = 2*i - 1
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = ConstraintList(rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(len(model.c), 2)

    def test_rule_option1a(self):
        """Test rule option"""
        model = self.create_model()
        @simple_constraintlist_rule
        def f(model, i):
            if i > 4:
                return None
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = ConstraintList(rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(model.c[2](), 16)
        self.assertEqual(len(model.c), 4)

    def test_rule_option2a(self):
        """Test rule option"""
        model = self.create_model()
        @simple_constraintlist_rule
        def f(model, i):
            if i > 2:
                return None
            i = 2*i - 1
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = ConstraintList(rule=f)
        
        self.assertEqual(model.c[1](), 8)
        self.assertEqual(len(model.c), 2)

    def test_rule_option3(self):
        """Test rule option"""
        model = self.create_model()
        model.y = Var(initialize=2)
        def f(model):
            yield model.y <= 0
            yield 2*model.y <= 0
            yield 2*model.y <= 0
            yield ConstraintList.End
        model.c = ConstraintList(rule=f)
        self.assertEqual(len(model.c), 3)
        self.assertEqual(model.c[1](), 2)
        model.d = ConstraintList(rule=f(model))
        self.assertEqual(len(model.d), 3)
        self.assertEqual(model.d[1](), 2)

    def test_rule_option4(self):
        """Test rule option"""
        model = self.create_model()
        model.y = Var(initialize=2)
        model.c = ConstraintList(rule=((i+1)*model.y >= 0 for i in xrange(3)))
        self.assertEqual(len(model.c), 3)
        self.assertEqual(model.c[1](), 2)

    def test_dim(self):
        """Test dim method"""
        model = self.create_model()
        model.c = ConstraintList(noruleinit=True)
        
        self.assertEqual(model.c.dim(),1)

    def test_keys(self):
        """Test keys method"""
        model = self.create_model()
        model.c = ConstraintList(noruleinit=True)
        
        self.assertEqual(len(model.c.keys()),0)

    def test_len(self):
        """Test len method"""
        model = self.create_model()
        model.c = ConstraintList(noruleinit=True)
        
        self.assertEqual(len(model.c),0)


class Test2DArrayCon(unittest.TestCase):

    def create_model(self):
        model = ConcreteModel()
        model.A = Set(initialize=[1,2])
        return model

    def test_rule_option(self):
        """Test rule option"""
        model = self.create_model()
        def f(model, i, j):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,model.A,rule=f)
        
        self.assertEqual(model.c[1,1](), 8)
        self.assertEqual(model.c[2,1](), 16)

    def test_old_rule_option(self):
        """Test rule option"""
        model = self.create_model()
        buffer = LogBuffer('pyomo.core', logging.WARNING)
        def f(model, i, j):
            ans=0
            for j in model.x:
                ans = ans + model.x[j]
            ans *= i
            ans = ans <= 0
            ans = ans >= 0
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(model.A,model.A,rule=f)
        
        self.assertEqual(model.c[1,1](), 8)
        self.assertEqual(model.c[2,1](), 16)

    def test_dim(self):
        """Test dim method"""
        model = self.create_model()
        model.c = Constraint(model.A,model.A, noruleinit=True)
        
        self.assertEqual(model.c.dim(),2)

    def test_keys(self):
        """Test keys method"""
        model = self.create_model()
        model.c = Constraint(model.A,model.A, noruleinit=True)
        
        self.assertEqual(len(model.c.keys()),0)

    def test_len(self):
        """Test len method"""
        model = self.create_model()
        model.c = Constraint(model.A,model.A, noruleinit=True)
        
        self.assertEqual(len(model.c),0)
        """Test rule option"""
        def f(model):
            ans=0
            for i in model.x:
                ans = ans + model.x[i]
            ans = ans==2
            return ans
        model.x = Var(RangeSet(1,4),initialize=2)
        model.c = Constraint(rule=f)
        
        self.assertEqual(len(model.c),1)

class MiscConTests(unittest.TestCase):

    def test_slack_methods(self):
        model = ConcreteModel()
        model.x = Var(initialize=2.0)
        L = -1.0
        U = 5.0
        model.cL = Constraint(expr=model.x**2 >= L)
        self.assertEqual(model.cL.lslack(), -5.0)
        self.assertEqual(model.cL.uslack(), float('inf'))
        model.cU = Constraint(expr=model.x**2 <= U)
        self.assertEqual(model.cU.lslack(), float('-inf'))
        self.assertEqual(model.cU.uslack(), 1.0)
        model.cR = Constraint(expr=L <= model.x**2 <= U)
        self.assertEqual(model.cR.lslack(), -5.0)
        self.assertEqual(model.cR.uslack(), 1.0)

    def test_constructor(self):
        a = Constraint(name="b", noruleinit=True)
        self.assertEqual(a.name,"b")
        try:
            a = Constraint(foo="bar", noruleinit=True)
            self.fail("Can't specify an unexpected constructor option")
        except ValueError:
            pass

    def test_contains(self):
        model=ConcreteModel()
        model.a=Set(initialize=[1,2,3])
        model.b=Constraint(model.a)
        
        self.assertEqual(2 in model.b,False)
        tmp=[]
        for i in model.b:
            tmp.append(i)
        self.assertEqual(len(tmp),0)

    def test_set_get(self):
        a = Constraint(noruleinit=True)
        a.construct()
        #try:
            #a.value = 1
            #self.fail("Can't set value attribute")
        #except AttributeError:
            #pass
        self.assertEqual(a(),None)

    def test_rule(self):
        def rule1(model):
            return Constraint.Skip
        model = ConcreteModel()
        try:
            model.o = Constraint(rule=rule1)
        except Exception:
            e = sys.exc_info()[1]
            self.fail("Failure to create empty constraint: %s" % str(e))
        #
        def rule1(model):
            return (0.0,model.x,2.0)
        model = ConcreteModel()
        model.x = Var(initialize=1.1)
        model.o = Constraint(rule=rule1)
        
        model.reset()
        self.assertEqual(model.o(),1.1)
        #
        def rule1(model, i):
            return Constraint.Skip
        model = ConcreteModel()
        model.a = Set(initialize=[1,2,3])
        try:
            model.o = Constraint(model.a,rule=rule1)
        except Exception:
            self.fail("Error generating empty constraint")

        model.reset()
        #
        def rule1(model):
            return (0.0,1.1,2.0,None)
        model = ConcreteModel()
        try:
            model.o = Constraint(rule=rule1)
            self.fail("Can only return tuples of length 2 or 3")
        except ValueError:
            pass

    def test_tuple_constraint_create(self):
        def rule1(model):
            return (0.0,model.x)
        model = ConcreteModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        
        #
        def rule1(model):
            return (model.y,model.x,model.z)
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #

    def test_expression_constructor_coverage(self):
        def rule1(model):
            expr = model.x
            expr = expr == 0.0
            expr = expr >= 1.0
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(TypeError, model.create)
        #
        def rule1(model):
            expr = model.U >= model.x
            expr = expr >= model.L
            return expr
        model = ConcreteModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.U = Param(initialize=1)
        model.o = Constraint(rule=rule1)
        
        #
        def rule1(model):
            expr = model.x <= model.z
            expr = expr >= model.y
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x >= model.z
            expr = model.y >= expr
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.y <= model.x
            expr = model.y >= expr
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x >= model.L
            return expr
        model = ConcreteModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        
        #
        def rule1(model):
            expr = model.U >= model.x
            return expr
        model = ConcreteModel()
        model.x = Var()
        model.U = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        

        #
        def rule1(model):
            expr=model.x
            expr = expr == 0.0
            expr = expr <= 1.0
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(TypeError, model.create)
        #
        def rule1(model):
            expr = model.U <= model.x
            expr = expr <= model.L
            return expr
        model = ConcreteModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.U = Param(initialize=1)
        model.o = Constraint(rule=rule1)
        
        #
        def rule1(model):
            expr = model.x >= model.z
            expr = expr <= model.y
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x <= model.z
            expr = model.y <= expr
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.z = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.y >= model.x
            expr = model.y <= expr
            return expr
        model = AbstractModel()
        model.x = Var()
        model.y = Var()
        model.o = Constraint(rule=rule1)
        self.assertRaises(ValueError, model.create)
        #
        def rule1(model):
            expr = model.x <= model.L
            return expr
        model = ConcreteModel()
        model.x = Var()
        model.L = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        
        #
        def rule1(model):
            expr = model.U <= model.x
            return expr
        model = ConcreteModel()
        model.x = Var()
        model.U = Param(initialize=0)
        model.o = Constraint(rule=rule1)
        

        #
        def rule1(model):
            return model.x+model.x
        model = ConcreteModel()
        model.x = Var()
        try:
            model.o = Constraint(rule=rule1)
            self.fail("Cannot return an unbounded expression")
        except ValueError:
            pass
        #

if __name__ == "__main__":
    unittest.main()

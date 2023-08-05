#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

import copy

import pyutilib.th as unittest
from pyomo.environ import *
from six import StringIO

class TestExpressionData(unittest.TestCase):
    
    # The copy method must be invoked on expression container to obtain
    # a shollow copy of the class, the underlying expression remains
    # a reference.
    def test_copy(self):
        model = ConcreteModel()
        model.a = Var(initialize=5)
        model.b = Var(initialize=10)

        model.expr1 = Expression(initialize=model.a)
        
        # Do a shallow copy, the same underlying expression is still referenced
        expr2 = copy.copy(model.expr1)
        self.assertEqual( model.expr1(), 5 )
        self.assertEqual( expr2(), 5 )
        self.assertEqual( id(model.expr1.value), id(expr2.value) )

        # Do an in place modification the expression
        model.expr1.value.value = 1
        self.assertEqual( model.expr1(), 1 )
        self.assertEqual( expr2(), 1 )
        self.assertEqual( id(model.expr1.value), id(expr2.value) )

        # Update the expression value on expr1 only
        model.expr1.value = model.b
        self.assertEqual( model.expr1(), 10 )
        self.assertEqual( expr2(), 1 )
        self.assertNotEqual( id(model.expr1.value), id(expr2.value) )

        model.a.value = 5
        model.b.value = 10
        model.del_component('expr1')
        model.expr1 = Expression(initialize=model.a + model.b)

        # Do a shallow copy, the same underlying expression is still referenced
        expr2 = copy.copy(model.expr1)
        self.assertEqual( model.expr1(), 15 )
        self.assertEqual( expr2(), 15 )
        self.assertEqual( id(model.expr1.value), id(expr2.value) )
        self.assertEqual( id(model.expr1.value._args[0]),
                          id(expr2.value._args[0]) )
        self.assertEqual( id(model.expr1.value._args[1]),
                          id(expr2.value._args[1]) )


        # Do an in place modification the expression
        # This causes cloning due to reference counting
        model.a.value = 0
        self.assertEqual( model.expr1(), 10 )
        self.assertEqual( expr2(), 10 )
        self.assertEqual( id(model.expr1.value), id(expr2.value) )
        self.assertEqual( id(model.expr1.value._args[0]),
                          id(expr2.value._args[0]) )
        self.assertEqual( id(model.expr1.value._args[1]),
                          id(expr2.value._args[1]) )


        # Do an in place modification the expression
        # This causes cloning due to reference counting
        model.expr1.value += 1
        self.assertEqual( model.expr1(), 11 )
        self.assertEqual( expr2(), 10 )
        self.assertNotEqual( id(model.expr1.value), id(expr2.value) )

    # test that an object is properly deepcopied when the model is cloned
    def test_model_clone(self):
        model = ConcreteModel()
        model.x = Var(initialize=2.0)
        model.y = Var(initialize=0.0)
        model.ec = Expression(initialize=model.x**2+1)
        model.obj = Objective(expr=model.y+model.ec)
        self.assertEqual(model.obj.expr(),5.0)
        self.assertTrue(id(model.ec) in [id(e) for e in model.obj.expr._args])
        inst = model.clone()
        self.assertEqual(inst.obj.expr(),5.0)
        self.assertTrue(id(inst.ec) in [id(e) for e in inst.obj.expr._args])
        self.assertNotEqual(id(model.ec), id(inst.ec))
        self.assertFalse(id(inst.ec) in [id(e) for e in model.obj.expr._args])

    def test_is_constant(self):
        model = ConcreteModel()
        model.x = Var(initialize=1.0)
        model.p = Param(initialize=1.0)
        model.ec = Expression(initialize=model.x)
        self.assertEqual(model.ec.is_constant(), False)
        self.assertEqual(model.ec.value.is_constant(), False)
        model.ec.value = model.p
        self.assertEqual(model.ec.is_constant(), False)
        self.assertEqual(model.ec.value.is_constant(), True)

    def test_polynomial_degree(self):
        model = ConcreteModel()
        model.x = Var(initialize=1.0)
        model.ec = Expression(initialize=model.x)
        self.assertEqual( model.ec.polynomial_degree(), 
                          model.ec.value.polynomial_degree() )
        self.assertEqual(model.ec.polynomial_degree(), 1)
        model.ec.value = model.x**2
        self.assertEqual( model.ec.polynomial_degree(), 
                          model.ec.value.polynomial_degree())
        self.assertEqual( model.ec.polynomial_degree(), 2 )


    def test_init_concrete(self):
        model = ConcreteModel()
        model.y = Var(initialize=0.0)
        model.x = Var(initialize=1.0)

        model.ec = Expression(initialize=0)
        model.obj = Objective(expr=1.0+model.ec)
        self.assertEqual(model.obj.expr(),1.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e = 1.0
        model.ec.value = e
        self.assertEqual(model.obj.expr(),2.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        model.ec.value = e
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))

        model.del_component('obj')
        model.del_component('ec')
        model.ec = Expression(initialize=model.y)
        model.obj = Objective(expr=1.0+model.ec)
        self.assertEqual(model.obj.expr(),1.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e = 1.0
        model.ec.value = e
        self.assertEqual(model.obj.expr(),2.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        model.ec.value = e
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))

        model.del_component('obj')
        model.del_component('ec')
        model.y.value = -1
        model.ec = Expression(initialize=model.y+1.0)
        model.obj = Objective(expr=1.0+model.ec)
        self.assertEqual(model.obj.expr(),1.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e = 1.0
        model.ec.value = e
        self.assertEqual(model.obj.expr(),2.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        model.ec.value = e
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))

    def test_init_abstract(self):
        model = AbstractModel()
        model.y = Var(initialize=0.0)
        model.x = Var(initialize=1.0)
        model.ec = Expression(initialize=0.0)

        def obj_rule(model):
            return 1.0+model.ec
        model.obj = Objective(rule=obj_rule)
        inst = model.create()
        self.assertEqual(inst.obj.expr(),1.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e = 1.0
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),2.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))

        model.del_component('obj')
        model.ec = Expression(initialize=0.0)
        def obj_rule(model):
            return 1.0+model.ec
        model.obj = Objective(rule=obj_rule)
        inst = model.create()
        self.assertEqual(inst.obj.expr(),1.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e = 1.0
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),2.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))

        model.del_component('obj')
        model.ec = Expression(initialize=0.0)
        def obj_rule(model):
            return 1.0+model.ec
        model.obj = Objective(rule=obj_rule)
        inst = model.create()
        self.assertEqual(inst.obj.expr(),1.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e = 1.0
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),2.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))

class TestExpression(unittest.TestCase):

    def setUp(self):
        TestExpression._save = pyomo.core.base.expr.TO_STRING_VERBOSE
        # Tests can choose what they want - this just makes sure that
        #things are restored after the tests run.
        #pyomo.core.base.expr.TO_STRING_VERBOSE = True

    def tearDown(self):
        pyomo.core.base.expr.TO_STRING_VERBOSE = TestExpression._save

    def test_init_concrete_indexed(self):
        model = ConcreteModel()
        model.y = Var(initialize=0.0)
        model.x = Var([1,2,3],initialize=1.0)

        model.ec = Expression([1,2,3],initialize=1.0)
        model.obj = Objective(expr=1.0+summation(model.ec, index=[1,2,3]))
        self.assertEqual(model.obj.expr(),4.0)
        model.ec[1].value = 2.0
        self.assertEqual(model.obj.expr(),5.0)

    def test_init_concrete_nonindexed(self):
        model = ConcreteModel()
        model.y = Var(initialize=0.0)
        model.x = Var(initialize=1.0)

        model.ec = Expression(initialize=0)
        model.obj = Objective(expr=1.0+model.ec)
        self.assertEqual(model.obj.expr(),1.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e = 1.0
        model.ec.value = e
        self.assertEqual(model.obj.expr(),2.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        model.ec.value = e
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))

        model.del_component('obj')
        model.del_component('ec')
        model.ec = Expression(initialize=model.y)
        model.obj = Objective(expr=1.0+model.ec)
        self.assertEqual(model.obj.expr(),1.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e = 1.0
        model.ec.value = e
        self.assertEqual(model.obj.expr(),2.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        model.ec.value = e
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))

        model.del_component('obj')
        model.del_component('ec')
        model.y.value = -1
        model.ec = Expression(initialize=model.y+1.0)
        model.obj = Objective(expr=1.0+model.ec)
        self.assertEqual(model.obj.expr(),1.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e = 1.0
        model.ec.value = e
        self.assertEqual(model.obj.expr(),2.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        model.ec.value = e
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))
        e += model.x
        self.assertEqual(model.obj.expr(),3.0)
        self.assertEqual(id(model.obj.expr._args[0]),id(model.ec))

    def test_init_abstract_indexed(self):
        model = AbstractModel()
        model.ec = Expression([1,2,3],initialize=1.0)
        model.obj = Objective(rule=lambda m: 1.0+summation(m.ec,index=[1,2,3]))
        inst = model.create()
        self.assertEqual(inst.obj.expr(),4.0)
        inst.ec[1].value = 2.0
        self.assertEqual(inst.obj.expr(),5.0)

    def test_init_abstract_nonindexed(self):
        model = AbstractModel()
        model.y = Var(initialize=0.0)
        model.x = Var(initialize=1.0)
        model.ec = Expression(initialize=0.0)

        def obj_rule(model):
            return 1.0+model.ec
        model.obj = Objective(rule=obj_rule)
        inst = model.create()
        self.assertEqual(inst.obj.expr(),1.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e = 1.0
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),2.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))

        model.del_component('obj')
        model.del_component('ec')
        model.ec = Expression(initialize=0.0)
        def obj_rule(model):
            return 1.0+model.ec
        model.obj = Objective(rule=obj_rule)
        inst = model.create()
        self.assertEqual(inst.obj.expr(),1.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e = 1.0
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),2.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))

        model.del_component('obj')
        model.del_component('ec')
        model.ec = Expression(initialize=0.0)
        def obj_rule(model):
            return 1.0+model.ec
        model.obj = Objective(rule=obj_rule)
        inst = model.create()
        self.assertEqual(inst.obj.expr(),1.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e = 1.0
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),2.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        inst.ec.value = e
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))
        e += inst.x
        self.assertEqual(inst.obj.expr(),3.0)
        self.assertEqual(id(inst.obj.expr._args[0]),id(inst.ec))

    def test_pprint_oldStyle(self):
        pyomo.core.base.expr.TO_STRING_VERBOSE = True

        model = ConcreteModel()
        model.x = Var()
        model.e = Expression(initialize=model.x+2.0)
        model.E = Expression([1,2],initialize=model.x**2+1)
        expr = model.e*model.x**2 + model.E[1]

        output = \
"""\
sum( prod( num=( e{sum( 2.0 , x )} , pow( x , 2.0 ) ) ) , E[1]{sum( 1 , pow( x , 2.0 ) )} )
e : Size=1, Index=None
    Key  : Expression
    None : sum( 2.0 , x )
E : Size=2, Index=E_index
    Key : Expression
      1 : sum( 1 , pow( x , 2.0 ) )
      2 : sum( 1 , pow( x , 2.0 ) )
"""
        out = StringIO()
        out.write(str(expr)+"\n")
        model.e.pprint(ostream=out)
        #model.E[1].pprint(ostream=out)
        model.E.pprint(ostream=out)
        self.assertEqual(output, out.getvalue())

        model.e.value = 1.0
        model.E[1].value = 2.0
        output = \
"""\
sum( prod( num=( e{1.0} , pow( x , 2.0 ) ) ) , E[1]{2.0} )
e : Size=1, Index=None
    Key  : Expression
    None :        1.0
E : Size=2, Index=E_index
    Key : Expression
      1 : 2.0
      2 : sum( 1 , pow( x , 2.0 ) )
"""
        out = StringIO()
        out.write(str(expr)+"\n")
        model.e.pprint(ostream=out)
        #model.E[1].pprint(ostream=out)
        model.E.pprint(ostream=out)
        self.assertEqual(output, out.getvalue())


        model.e.value = None
        model.E[1].value = None
        output = \
"""\
sum( prod( num=( e{Undefined} , pow( x , 2.0 ) ) ) , E[1]{Undefined} )
e : Size=1, Index=None
    Key  : Expression
    None :  Undefined
E : Size=2, Index=E_index
    Key : Expression
      1 : Undefined
      2 : sum( 1 , pow( x , 2.0 ) )
"""
        out = StringIO()
        out.write(str(expr)+"\n")
        model.e.pprint(ostream=out)
        #model.E[1].pprint(ostream=out)
        model.E.pprint(ostream=out)
        self.assertEqual(output, out.getvalue())


    def test_pprint_newStyle(self):
        pyomo.core.base.expr.TO_STRING_VERBOSE = False

        model = ConcreteModel()
        model.x = Var()
        model.e = Expression(initialize=model.x+2.0)
        model.E = Expression([1,2],initialize=model.x**2+1)
        expr = model.e*model.x**2 + model.E[1]

        output = \
"""\
( 2.0 + x ) * x**2.0 + 1 + x**2.0
e : Size=1, Index=None
    Key  : Expression
    None : 2.0 + x
E : Size=2, Index=E_index
    Key : Expression
      1 : 1 + x**2.0
      2 : 1 + x**2.0
"""
        out = StringIO()
        out.write(str(expr)+"\n")
        model.e.pprint(ostream=out)
        #model.E[1].pprint(ostream=out)
        model.E.pprint(ostream=out)
        self.assertEqual(output, out.getvalue())

        model.e.value = 1.0
        model.E[1].value = 2.0
        output = \
"""\
1.0 * x**2.0 + 2.0
e : Size=1, Index=None
    Key  : Expression
    None :        1.0
E : Size=2, Index=E_index
    Key : Expression
      1 : 2.0
      2 : 1 + x**2.0
"""
        out = StringIO()
        out.write(str(expr)+"\n")
        model.e.pprint(ostream=out)
        #model.E[1].pprint(ostream=out)
        model.E.pprint(ostream=out)
        self.assertEqual(output, out.getvalue())


        model.e.value = None
        model.E[1].value = None
        output = \
"""\
Undefined * x**2.0 + Undefined
e : Size=1, Index=None
    Key  : Expression
    None :  Undefined
E : Size=2, Index=E_index
    Key : Expression
      1 : Undefined
      2 : 1 + x**2.0
"""
        out = StringIO()
        out.write(str(expr)+"\n")
        model.e.pprint(ostream=out)
        #model.E[1].pprint(ostream=out)
        model.E.pprint(ostream=out)
        self.assertEqual(output, out.getvalue())

    def test_len(self):
        model = AbstractModel()
        model.e = Expression()
        
        self.assertEqual(len(model.e), 0)
        inst = model.create()
        self.assertEqual(len(inst.e), 1)

    def test_None_key(self):
        model = AbstractModel()
        model.e = Expression()
        inst = model.create()
        self.assertEqual(id(inst.e), id(inst.e[None]))


if __name__ == "__main__":
    unittest.main()


    

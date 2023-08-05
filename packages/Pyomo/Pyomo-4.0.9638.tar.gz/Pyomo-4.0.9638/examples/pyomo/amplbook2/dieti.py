#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________
#
# Imports
#
from pyomo.core import *

#
# Setup
#

model = AbstractModel()

model.NUTR = Set()

model.FOOD = Set()

model.cost = Param(model.FOOD, within=NonNegativeReals)

model.f_min = Param(model.FOOD, within=NonNegativeReals)

def f_max_valid (model, value, j):
    return value > model.f_min[j]
model.f_max = Param(model.FOOD, validate=f_max_valid)

model.n_min = Param(model.NUTR, within=NonNegativeReals)

def paramn_max (model, value, i):
    return value > model.n_min[i]
model.n_max = Param(model.NUTR, validate=paramn_max)

model.amt = Param(model.NUTR, model.FOOD, within=NonNegativeReals)

def Buy_bounds(model,i):
    return (model.f_min[i],model.f_max[i])
model.Buy = Var(model.FOOD, bounds=Buy_bounds, domain=Integers)

def Objective_rule(model):
    return summation(model.cost, model.Buy)
model.totalcost = Objective(rule=Objective_rule)

def Diet_rule(model, i):
    expr = 0
    for j in model.FOOD:
        expr = expr + model.amt[i,j] * model.Buy[j]
    return (model.n_min[i], expr, model.n_max[i])
model.Diet = Constraint(model.NUTR, rule=Diet_rule)

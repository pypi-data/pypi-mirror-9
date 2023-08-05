#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

from pyomo.environ import *
from pyomo.dae import *
from pyomo.opt import SolverFactory
from pyomo.dae.plugins.finitedifference import Finite_Difference_Transformation
from pyomo.dae.plugins.colloc import Collocation_Discretization_Transformation
from Optimal_Control import m

instance = m.create()

# Discretize model using Backward Finite Difference method
#discretize = Finite_Difference_Transformation()
#disc_instance = discretize.apply(instance,nfe=20,scheme='BACKWARD')

# Discretize model using Orthogonal Collocation
discretize = Collocation_Discretization_Transformation()
disc_instance = discretize.apply(instance,nfe=7,ncp=6,scheme='LAGRANGE-RADAU')
# Will reimplement this method in future release of pyomo.dae
# disc_instance = discretize.reduce_collocation_points(var=instance.u,
# 	ncp=2, diffset=instance.t)

solver='ipopt'
opt=SolverFactory(solver)

results = opt.solve(disc_instance,tee=True)
disc_instance.load(results)

x1 = []
x2 = []
u = []
t=[]

print sorted(disc_instance.t)

for i in sorted(disc_instance.t):
    t.append(i)
    x1.append(value(disc_instance.x1[i]))
    x2.append(value(disc_instance.x2[i]))
    u.append(value(disc_instance.u[i]))

import matplotlib.pyplot as plt

plt.plot(t,x1)
plt.plot(t,x2)
plt.show()

plt.plot(t,u)
plt.show()

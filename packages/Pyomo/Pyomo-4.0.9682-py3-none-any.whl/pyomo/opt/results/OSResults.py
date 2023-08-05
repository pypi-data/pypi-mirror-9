#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

__all__ = ['GeneralResult']

from pyomo.opt.results.container import *
from pyutilib.enum import Enum


class GeneralSubstatus(DataContainer):

    def __init__(self):
        DataContainer.__init__(self)
        self.declare('name', required=True)
        self.declare('description')


class GeneralStatus(DataContainer):

    Types = Enum('error', 'warning', 'normal')

    def __init__(self):
        DataContainer.__init__(self)
        self.declare('general_substatus', value=ListContainer(GeneralSubstatus), active=False)
        self.declare('description')
        self.declare('number_of_substatuses')
        self.declare('type', value=GeneralResult.Types.normal, required=True)


class GeneralResult(DataContainer):

    def __init__(self):
        DataContainer.__init__(self)
        self.declare('message')
        self.declare('service_URI')
        self.declare('service_name')
        self.declare('instance_name')
        self.declare('job_ID')
        self.declare('solver_invoked')
        self.declare('time_stamp')
        self.declare('general_status', value=GeneralStatus(), active=False)

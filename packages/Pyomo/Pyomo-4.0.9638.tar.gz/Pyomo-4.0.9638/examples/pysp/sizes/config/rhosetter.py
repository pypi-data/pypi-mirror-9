#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

def ph_rhosetter_callback(ph, scenario_tree, scenario):
   
   MyRhoFactor = 1.0

   root_node = scenario_tree.findRootNode()

   scenario_instance = scenario._instance
   symbol_map = scenario_instance._ScenarioTreeSymbolMap

   for i in scenario_instance.ProductSizes:

      ph.setRhoOneScenario(
         root_node,
         scenario,
         symbol_map.getSymbol(scenario_instance.ProduceSizeFirstStage[i]),
         scenario_instance.SetupCosts[i] * MyRhoFactor * 0.001)

      ph.setRhoOneScenario(
         root_node,
         scenario,
         symbol_map.getSymbol(scenario_instance.NumProducedFirstStage[i]),
         scenario_instance.UnitProductionCosts[i] * MyRhoFactor * 0.001)

      for j in scenario_instance.ProductSizes:
         if j <= i: 
            ph.setRhoOneScenario(
               root_node,
               scenario,
               symbol_map.getSymbol(scenario_instance.NumUnitsCutFirstStage[i,j]),
               scenario_instance.UnitReductionCost * MyRhoFactor * 0.001)

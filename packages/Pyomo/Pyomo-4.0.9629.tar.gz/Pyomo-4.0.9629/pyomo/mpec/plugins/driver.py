#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

# Deprecated

import sys
import time
from pyutilib.misc import Options, Container
from pyomo.core import *
from pyomo.util import pyomo_command
from pyomo.scripting.pyomo_command import create_parser
import pyomo.scripting.util
from pyomo.util.plugin import ExtensionPoint
from pyomo.scripting import pyomo_parser


def process_results(data, instance=None, results=None, opt=None):
    """
    Process optimization results.

    Required:
        instance:   Problem instance.
        results:    Optimization results object.
        opt:        Optimizer object.
    """
    #
    if data.options.log:
        print("")
        print("==========================================================")
        print("Solver Logfile:",opt.log_file)
        print("==========================================================")
        print("")
        INPUT = open(opt.log_file, "r")
        for line in INPUT:
            print(line,)
        INPUT.close()
    #
    try:
        # transform the results object into human-readable names.
        # IMPT: the resulting object won't be loadable - it's only for output.
        #transformed_results = instance.update_results(results)
        transformed_results = results
    except Exception:
        print("Problem updating solver results")
        raise
    #
    if not data.options.show_results:
        if data.options.save_results:
            results_file = data.options.save_results
        elif data.options.results_format == 'yaml':
            results_file = 'results.yml'
        else:
            results_file = 'results.json'
        transformed_results.write(filename=results_file, format=data.options.results_format)
        if not data.options.quiet:
            print("    Number of solutions: "+str(len(transformed_results.solution)))
            if len(transformed_results.solution) > 0:
                print("    Solution Information")
                print("      Gap: "+str(transformed_results.solution[0].gap))
                print("      Status: "+str(transformed_results.solution[0].status))
                if len(transformed_results.solution[0].objective) == 1:
                    key = transformed_results.solution[0].objective.keys()[0]
                    print("      Function Value: "+str(transformed_results.solution[0].objective[key].value))
            print("    Solver results file: "+results_file)
    #
    ep = ExtensionPoint(IPyomoScriptPrintResults)
    if False and len(ep) == 0:
        try:
            instance.load(results)
        except Exception:
            print("Problem loading solver results")
            raise
    if data.options.show_results:
        print("")
        transformed_results.write(num=1, format=data.options.results_format)
        print("")
    #
    if data.options.summary:
        print("")
        print("==========================================================")
        print("Solution Summary")
        print("==========================================================")
        if len(results.solution(0).variable) > 0:
            print("")
            display(instance)
            print("")
        else:
            print("No solutions reported by solver.")
    #
    for ep in ExtensionPoint(IPyomoScriptPrintResults):
        ep.apply( options=data.options, instance=instance, results=results )
    #
    for ep in ExtensionPoint(IPyomoScriptSaveResults):
        ep.apply( options=data.options, instance=instance, results=results )
    #
    if False and (pympler_available is True) and (data.options.profile_memory >= 1):
        global memory_data
        mem_used = muppy.get_size(muppy.get_objects())
        if mem_used > data.options.max_memory:
            data.options.max_memory = mem_used
        print("   Total memory = %d bytes following results processing" % mem_used)


def run_mpec(options=Options(), parser=None):
    import pyomo.environ
    data = Options(options=options)

    if options.version:
        from pyomo.util import driver
        driver.version_exec(None)
        return 0
    #
    if options.help_solvers:
        pyomo.scripting.util.print_solver_help(data)
        pyomo.scripting.util.finalize(data, model=None, instance=None, results=None)
        return Container()
    #
    if options.help_components:
        pyomo.scripting.util.print_components(data)
        return Container()
    #
    pyomo.scripting.util.setup_environment(data)
    #
    pyomo.scripting.util.apply_preprocessing(data, parser=parser)
    if data.error:
        pyomo.scripting.util.finalize(data, model=None, instance=None, results=None)
        return Container()                                   #pragma:nocover
    #
    model_data = pyomo.scripting.util.create_model(data)
    if (not options.debug and options.save_model) or options.only_instance:
        pyomo.scripting.util.finalize(data, model=model_data.model, instance=model_data.instance, results=None)
        return Container(instance=model_data.instance)
    #
    opt_data = pyomo.scripting.util.apply_optimizer(data, instance=model_data.instance)

    # this is hack-ish, and carries the following justification.
    # symbol maps are not pickle'able, and as a consequence, results
    # coming back from a pyro solver manager don't have a symbol map.
    # however, you need a symbol map to load the result into an 
    # instance. so, if it isn't there, construct it!
    if opt_data.results._symbol_map is None:
        from pyomo.core.base.symbol_map import symbol_map_from_instance
        opt_data.results._symbol_map = symbol_map_from_instance(model_data.instance)

    #
    process_results(data, instance=model_data.instance, results=opt_data.results, opt=opt_data.opt)
    #
    pyomo.scripting.util.apply_postprocessing(data, instance=model_data.instance, results=opt_data.results)
    #
    pyomo.scripting.util.finalize(data, model=model_data.model, instance=model_data.instance, results=opt_data.results)
    #
    return Container(options=options, instance=model_data.instance, results=opt_data.results)


def mpec_exec(args=None):
    return pyomo.scripting.util.run_command(command=run_mpec, parser=mpec_parser, args=args, name='mpec')

#
# Add a subparser for the pyomo command
#
mpec_parser = create_parser(
    pyomo_parser.add_subparser('mpec',
        func=mpec_exec,
        help='Analyze a MPEC model',
        description='This pyomo subcommand is used to analyze MPEC models.'
        ))


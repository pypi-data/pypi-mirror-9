#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

import logging
import os
import re
import sys

from six import iteritems

from pyutilib.common import ApplicationError
import pyutilib.subprocess
from pyutilib.misc import Bunch, Options
from pyutilib.services import register_executable, registered_executable
from pyutilib.services import TempfileManager

import pyomo.util.plugin
from pyomo.opt import *
from pyomo.opt.base.solvers import _extract_version
from pyomo.opt.solver import SystemCallSolver

logger = logging.getLogger('pyomo.solvers')

glpk_file_flag=None
_glpk_version = None
def configure_glpk():
    global glpk_file_flag
    global _glpk_version
    if glpk_file_flag is not None:
        return
    glpk_file_flag = False
    if registered_executable("glpsol") is None:
        return
    errcode, results = pyutilib.subprocess.run(
        [registered_executable('glpsol').get_path(), "--version"], timelimit=2)
    if errcode == 0:
        _glpk_version = _extract_version(results)
        glpk_file_flag = _glpk_version >= (4,42,0,0)


# Not sure how better to get these constants, but pulled from GLPK
# documentation and source code (include/glpk.h)

   # status of auxiliary / structural variables
GLP_BS = 1   # inactive constraint / basic variable
GLP_NL = 2   # active constraint or non-basic variable on lower bound
GLP_NU = 3   # active constraint or non-basic variable on upper bound
GLP_NF = 4   # active free row or non-basic free variable
GLP_NS = 5   # active equality constraint or non-basic fixed variable

   # solution status
GLP_UNDEF  = 1  # solution is undefined
GLP_FEAS   = 2  # solution is feasible
GLP_INFEAS = 3  # solution is infeasible
GLP_NOFEAS = 4  # no feasible solution exists
GLP_OPT    = 5  # solution is optimal
GLP_UNBND  = 6  # solution is unbounded


class GLPK(OptSolver):
    """The GLPK LP/MIP solver"""

    pyomo.util.plugin.alias('glpk', doc='The GLPK LP/MIP solver')

    def __new__(cls, *args, **kwds):
        try:
            mode = kwds['solver_io']
            if mode is None:
                mode = 'lp'
            del kwds['solver_io']
        except KeyError:
            mode = 'lp'
        #
        if mode  == 'lp':
            if glpk_file_flag:
                return SolverFactory('_glpk_shell', **kwds)
            else:
                return SolverFactory('_glpk_shell_old', **kwds)
        if mode == 'python':
            opt = SolverFactory('_glpk_direct', **kwds)
            if opt is None:
                logger.error('Python API for GLPK is not installed')
                return
            return opt
        #
        if mode == 'os':
            opt = SolverFactory('_ossolver', **kwds)
        else:
            logger.error('Unknown IO type: %s' % mode)
            return
        opt.set_options('solver=glpsol')
        return opt


class GLPKSHELL ( SystemCallSolver ):
    """Shell interface to the GLPK LP/MIP solver"""

    pyomo.util.plugin.alias('_glpk_shell', doc='Shell interface to the GNU Linear Programming Kit')

    def __init__ ( self, **kwargs ):
        #
        # Call base constructor
        #
        kwargs['type'] = 'glpk'
        SystemCallSolver.__init__( self, **kwargs )
        #
        # Valid problem formats, and valid results for each format
        #
        self._valid_problem_formats = [ ProblemFormat.cpxlp, ProblemFormat.mps, ProblemFormat.mod ]
        self._valid_result_formats = {
          ProblemFormat.mod:   ResultsFormat.soln,
          ProblemFormat.cpxlp: ResultsFormat.soln,
          ProblemFormat.mps:   ResultsFormat.soln,
        }
        self.set_problem_format(ProblemFormat.cpxlp)

        # Note: Undefined capabilities default to 'None'
        self._capabilities = Options()
        self._capabilities.linear = True
        self._capabilities.integer = True

    def _default_results_format(self, prob_format):
        return ResultsFormat.soln

    def executable ( self ):
        executable = registered_executable('glpsol')
        if executable is None:
            msg = "Could not locate the 'glpsol' executable, which is "          \
                  "required for solver '%s'"
            logger.warning(msg % self.name)
            self.enable = False
            return None

        return executable.get_path()

    def version(self):
        """
        Returns a tuple describing the solver executable version.
        """
        if _glpk_version is None:
            return _extract_version('')
        return _glpk_version

    def create_command_line ( self, executable, problem_files ):
        #
        # Define log file
        #
        if self.log_file is None:
            self.log_file = TempfileManager.create_tempfile(suffix='.glpk.log')

        #
        # Define solution file
        #
        self._glpfile = TempfileManager.create_tempfile(suffix='.glpk.glp')
        self._rawfile = TempfileManager.create_tempfile(suffix='.glpk.raw')
        self.soln_file = self._rawfile
        self.results_file = self.soln_file

        #
        # Define command line
        #
        cmd = [executable]
        if self._timer:
            cmd.insert(0, self._timer)
        for key in self.options:
            opt = self.options[ key ]
            if (opt.__class__ is str) and (opt.strip() == ''):
                # Handle the case for options that must be
                # specified without a value
                cmd.append("--%s" % key)
            else:
                cmd.extend(["--%s" % key, str(opt)])
            #if isinstance(opt, basestring) and ' ' in opt:
            #    cmd.append('--%s "%s"' % (key, str(opt)) )
            #else:
            #    cmd.append('--%s %s' % (key, str(opt)) )

        if self._timelimit is not None and self._timelimit > 0.0:
            cmd.extend(['--tmlim', str(self._timelimit)])

        cmd.extend(['--write', self._rawfile])
        cmd.extend(['--wglp', self._glpfile])

        if self._problem_format == ProblemFormat.cpxlp:
            cmd.extend(['--cpxlp', problem_files[0]])
        elif self._problem_format == ProblemFormat.mps:
            cmd.extend(['--freemps', problem_files[0]])
        elif self._problem_format == ProblemFormat.mod:
            cmd.extend(['--math', problem_files[0]])
            for fname in problem_files[1:]:
                cmd.extend(['--data', fname])

        return Bunch(cmd=cmd, log_file=self.log_file, env=None)


    def process_logfile(self):
        """
        Process logfile
        """
        results = SolverResults()

        # For the lazy programmer, handle long variable names
        prob   = results.problem
        solv   = results.solver
        solv.termination_condition = TerminationCondition.unknown
        stats  = results.solver.statistics
        bbound = stats.branch_and_bound

        prob.upper_bound = float('inf')
        prob.lower_bound = float('-inf')
        bbound.number_of_created_subproblems = 0
        bbound.number_of_bounded_subproblems = 0

        with open( self.log_file, 'r' ) as output:
            for line in output:
                toks = line.split()
                if 'tree is empty' in line:
                    bbound.number_of_created_subproblems = toks[-1][:-1]
                    bbound.number_of_bounded_subproblems = toks[-1][:-1]
                elif len(toks) == 2 and toks[0] == "sys":
                    solv.system_time = toks[1]
                elif len(toks) == 2 and toks[0] == "user":
                    solv.user_time = toks[1]
                elif len(toks) > 2 and (toks[0], toks[2]) == ("TIME", "EXCEEDED;"):
                    solv.termination_condition = TerminationCondition.maxTimeLimit
                elif len(toks) > 5 and (toks[:6] == ['PROBLEM', 'HAS', 'NO', 'DUAL', 'FEASIBLE', 'SOLUTION']):
                    solv.termination_condition = TerminationCondition.unbounded
                elif len(toks) > 5 and (toks[:6] == ['PROBLEM', 'HAS', 'NO', 'PRIMAL', 'FEASIBLE', 'SOLUTION']):
                    solv.termination_condition = TerminationCondition.infeasible
                elif len(toks) > 4 and (toks[:5] == ['PROBLEM', 'HAS', 'NO', 'FEASIBLE', 'SOLUTION']):
                    solv.termination_condition = TerminationCondition.infeasible
                elif len(toks) > 6 and (toks[:7] == ['LP', 'RELAXATION', 'HAS', 'NO', 'DUAL', 'FEASIBLE', 'SOLUTION']):
                    solv.termination_condition = TerminationCondition.unbounded

        return results


    def _glpk_get_solution_status ( self, status ):
        if   GLP_OPT    == status: return SolutionStatus.optimal
        elif GLP_FEAS   == status: return SolutionStatus.feasible
        elif GLP_INFEAS == status: return SolutionStatus.infeasible
        elif GLP_NOFEAS == status: return SolutionStatus.infeasible
        elif GLP_UNBND  == status: return SolutionStatus.unbounded
        elif GLP_UNDEF  == status: return SolutionStatus.other
        raise RuntimeError("Unknown solution status returned by GLPK solver")


    def process_soln_file ( self, results ):
        soln  = None
        pdata = self._glpfile
        psoln = self._rawfile

        prob = results.problem
        solv = results.solver

        prob.name = 'unknown'   # will ostensibly get updated

        # Step 1: Make use of the GLPK's machine parseable format (--wglp) to
        #    collect variable and constraint names.
        glp_line_count = ' -- File not yet opened'

        # The trick for getting the variable names correctly matched to their
        # values is the note that the --wglp option outputs them in the same
        # order as the --write output.
        # Note that documentation for these formats is available from the GLPK
        # documentation of 'glp_read_prob' and 'glp_write_sol'
        variable_names = dict()    # cols
        constraint_names = dict()  # rows
        obj_name = 'objective'

        try:
            f = open( pdata, 'r')

            glp_line_count = 1
            pprob, ptype, psense, prows, pcols, pnonz = f.readline().split()
            prows = int( prows )  # fails if not a number; intentional
            pcols = int( pcols )  # fails if not a number; intentional
            pnonz = int( pnonz )  # fails if not a number; intentional

            if pprob != 'p' or \
               ptype not in ('lp', 'mip') or \
               psense not in ('max', 'min') or \
               prows < 0 or pcols < 0 or pnonz < 0:
                raise ValueError

            self.is_integer = ( 'mip' == ptype and True or False )
            prob.sense = 'min' == psense and ProblemSense.minimize or ProblemSense.maximize
            prob.number_of_constraints = prows
            prob.number_of_nonzeros    = pnonz
            prob.number_of_variables   = pcols

            extract_duals = False
            extract_reduced_costs = False
            for suffix in self.suffixes:
                flag = False
                if re.match(suffix, "dual"):
                    if not self.is_integer:
                        flag = True
                        extract_duals = True
                if re.match(suffix, "rc"):
                    if not self.is_integer:
                        flag = True
                        extract_reduced_costs = True
                if not flag:
                    # TODO: log a warning
                    pass

            for line in f:
                glp_line_count += 1
                tokens = line.split()
                switch = tokens.pop(0)

                if switch in ('a', 'e', 'i', 'j'):
                    pass
                elif 'n' == switch:  # naming some attribute
                    ntype = tokens.pop(0)
                    name  = tokens.pop()
                    if 'i' == ntype:      # row
                        row = tokens.pop()
                        constraint_names[ int(row) ] = name
                        # --write order == --wglp order; store name w/ row no
                    elif 'j' == ntype:    # var
                        col = tokens.pop()
                        variable_names[ int(col) ] = name
                        # --write order == --wglp order; store name w/ col no
                    elif 'z' == ntype:    # objective
                        obj_name = name
                    elif 'p' == ntype:    # problem name
                        prob.name = name
                    else:                 # anything else is incorrect.
                        raise ValueError

                else:
                    raise ValueError

            f.close()
        except Exception:
            e = sys.exc_info()[1]
            msg = "Error parsing solution description file, line %s: %s"
            raise ValueError(msg % (glp_line_count, str(e)))

        range_duals = {}
        # Step 2: Make use of the GLPK's machine parseable format (--write) to
        #    collect solution variable and constraint values.
        raw_line_count = ' -- File not yet opened'
        try:
            f = open( psoln, 'r')

            raw_line_count = 1
            prows, pcols = f.readline().split()
            prows = int( prows )  # fails if not a number; intentional
            pcols = int( pcols )  # fails if not a number; intentional

            raw_line_count = 2
            if self.is_integer:
                pstat, obj_val = f.readline().split()
            else:
                pstat, dstat, obj_val = f.readline().split()
                dstat = float( dstat ) # dual status of basic solution.  Ignored.

            pstat = float( pstat )       # fails if not a number; intentional
            obj_val = float( obj_val )   # fails if not a number; intentional
            soln_status = self._glpk_get_solution_status( pstat )

            if soln_status is SolutionStatus.infeasible:
                solv.termination_condition = TerminationCondition.infeasible

            elif soln_status is SolutionStatus.unbounded:
                solv.termination_condition = TerminationCondition.unbounded

            elif soln_status is SolutionStatus.other:
                if solv.termination_condition == TerminationCondition.unknown:
                    solv.termination_condition = TerminationCondition.other

            elif soln_status in ( SolutionStatus.optimal, SolutionStatus.feasible ):
                soln   = results.solution.add()
                soln.status = soln_status

                prob.lower_bound = obj_val
                prob.upper_bound = obj_val

                # TODO: Does a 'feasible' status mean that we're optimal?
                soln.gap=0.0
                solv.termination_condition = TerminationCondition.optimal
                

                # I'd like to choose the correct answer rather than just doing
                # something like commenting the obj_name line.  The point is that
                # we ostensibly could or should make use of the user's choice in
                # objective name.  In that vein I'd like to set the objective value
                # to the objective name.  This would make parsing on the user end
                # less 'arbitrary', as in the yaml key 'f'.  Weird
                soln.objective[ obj_name ] = obj_val

                if (self.is_integer is True) or (extract_duals is False):
                    # we use nothing from this section so just read in the
                    # lines and throw them away
                    for mm in range( 1, prows +1 ):
                        raw_line_count += 1
                        f.readline()
                else:
                    for mm in range( 1, prows +1 ):
                        raw_line_count += 1                    

                        rstat, rprim, rdual = f.readline().split()
                        rstat = float( rstat )
                        
                        cname = constraint_names[ mm ]
                        if 'ONE_VAR_CONSTANT' == cname[-16:]: continue

                        if cname.startswith('c_'):
                            soln.constraint[ cname ] = {"Dual":float(rdual)}
                        elif cname.startswith('r_l_'):
                            range_duals.setdefault(cname[4:],[0,0])[0] = float(rdual)
                        elif cname.startswith('r_u_'):
                            range_duals.setdefault(cname[4:],[0,0])[1] = float(rdual)

                for nn in range( 1, pcols +1 ):
                    raw_line_count += 1
                    if self.is_integer:
                        cprim = f.readline()      # should be a single number
                    else:
                        cstat, cprim, cdual = f.readline().split()
                        cstat = float( cstat )  # fails if not a number; intentional

                    vname = variable_names[ nn ]
                    if 'ONE_VAR_CONSTANT' == vname: continue
                    cprim = float( cprim )
                    if extract_reduced_costs is False:
                        soln.variable[ vname ] = {"Value" : cprim, "Id" : len(soln.variable)}
                    else:
                        soln.variable[ vname ] = {"Value" : cprim,
                                                  "Id" : len(soln.variable),
                                                  "Rc" : float(cdual)}

            f.close()
        except Exception:
            print(sys.exc_info()[1])
            msg = "Error parsing solution data file, line %d" % raw_line_count
            raise ValueError(msg)

        if not soln is None:
            # For the range constraints, supply only the dual with the largest
            # magnitude (at least one should always be numerically zero)
            scon = soln.Constraint
            for key,(ld,ud) in iteritems(range_duals):
                if abs(ld) > abs(ud):
                    scon['r_l_'+key] = {"Dual":ld}
                else:
                    scon['r_u_'+key] = {"Dual":ud}


register_executable( name='glpsol')

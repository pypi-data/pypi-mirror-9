#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

import pyutilib.dev.runtests
import sys
import os.path
import optparse
import pyomo.util

@pyomo.util.pyomo_command('test.pyomo', "Execute Pyomo tests")
def runPyomoTests():
    parser = optparse.OptionParser(usage='test.pyomo [options] <dirs>')

    parser.add_option('-d','--dir',
        action='store',
        dest='dir',
        default=None,
        help='Top-level source directory where the tests are applied.')
    parser.add_option('--cat','--category',
        action='append',
        dest='cats',
        default=[],
        help='Specify test categories.')
    parser.add_option('--all',
        action='store_true',
        dest='all_cats',
        default=False,
        help='All tests are executed.')
    parser.add_option('--cov','--coverage',
        action='store_true',
        dest='coverage',
        default=False,
        help='Indicate that coverage information is collected')
    parser.add_option('-v','--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Verbose output')
    parser.add_option('-o','--output',
        action='store',
        dest='output',
        default=None,
        help='Redirect output to a file')

    _options, args = parser.parse_args(sys.argv)

    if _options.output:
        outfile = os.path.abspath(_options.output)
    else:
        outfile = None
    if _options.dir is None:
        # the /src directory (for development installations)
        os.chdir( os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) )
    else:
        if os.path.exists(_options.dir):
            os.chdir( _options.dir )

    print("Running tests in directory %s" % os.getcwd())
    if _options.all_cats is True:
        _options.cats = []
    elif os.environ.get('PYUTILIB_UNITTEST_CATEGORIES',''):
        _options.cats = [x.strip() for x in 
                         os.environ['PYUTILIB_UNITTEST_CATEGORIES'].split(',')
                         if x.strip()]
    elif len(_options.cats) == 0:
        _options.cats = ['smoke']
    if 'all' in _options.cats:
        _options.cats = []
    if len(_options.cats) > 0:
        os.environ['PYUTILIB_UNITTEST_CATEGORIES'] = ",".join(_options.cats)
        print(" ... for test categories: "+ os.environ['PYUTILIB_UNITTEST_CATEGORIES'])
    elif 'PYUTILIB_UNITTEST_CATEGORIES' in os.environ:
        del os.environ['PYUTILIB_UNITTEST_CATEGORIES']
    options=[]
    if _options.coverage:
        options.append('--coverage')
    if _options.verbose:
        options.append('-v')
    if outfile:
        options.append('-o')
        options.append(outfile)
    if len(args) == 1:
        dirs=['pyomo*']
    else:
        dirs=[]
        for dir in args[1:]:
            if dir.startswith('-'):
                options.append(dir)
            if dir.startswith('pyomo'):
                if os.path.exists(dir):
                    dirs.append(dir)
                elif '.' in dir:
                    dirs.append(os.path.join('pyomo','pyomo',dir.split('.')[1]))
                else:
                    dirs.append(os.path.join('pyomo','pyomo'))
            else:
                if os.path.exists('pyomo.'+dir):
                    dirs.append('pyomo.'+dir)
                else:
                    dirs.append(os.path.join('pyomo','pyomo',dir))
        if len(dirs) == 0:
            dirs = ['pyomo*']

    pyutilib.dev.runtests.run('pyomo', ['runtests']+options+['-p','pyomo']+dirs)

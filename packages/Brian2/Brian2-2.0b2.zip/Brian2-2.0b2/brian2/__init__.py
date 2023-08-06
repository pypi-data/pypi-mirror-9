'''
Brian 2.0
'''
# Check basic dependencies
import sys
from distutils.version import StrictVersion
missing = []
try:
    import numpy
except ImportError as ex:
    sys.stderr.write('Importing numpy failed: %s\n' % ex)
    missing.append('numpy')
try:
    import scipy
except ImportError as ex:
    sys.stderr.write('Importing scipy failed: %s\n' % ex)
    missing.append('scipy')
try:
    import sympy
except ImportError as ex:
    sys.stderr.write('Importing sympy failed: %s\n' % ex)
    missing.append('sympy')
try:
    import pyparsing
except ImportError as ex:
    sys.stderr.write('Importing pyparsing failed: %s\n' % ex)
    missing.append('pyparsing')

if len(missing):
    raise ImportError('Some required dependencies are missing:\n' + ', '.join(missing))

try:
    from pylab import *
except ImportError:
    # Do the non-matplotlib pylab imports manually
    from numpy import *
    from numpy.fft import *
    from numpy.random import *
    from numpy.linalg import *
    import numpy.ma as ma
    # don't let numpy's datetime hide stdlib
    import datetime

# Make sure that Brian's unit-aware functions are used, even when directly
# using names prefixed with numpy or np
import brian2.numpy_ as numpy
import brian2.numpy_ as np

# delete some annoying names from the namespace
if 'x' in globals():
    del x
if 'f' in globals():
    del f
if 'rate' in globals():
    del rate

__docformat__ = "restructuredtext en"

__version__ = '2.0b2'
__release_date__ = '2015-03-11'

from brian2.only import *

# Check for outdated dependency versions
def _check_dependency_version(name, version):
    from core.preferences import prefs
    from utils.logger import get_logger
    logger = get_logger(__name__)

    module = sys.modules[name]
    if not isinstance(module.__version__, basestring):  # mocked module
        return
    if not StrictVersion(module.__version__) >= StrictVersion(version):
        message = '%s is outdated (got version %s, need version %s)' % (name,
                                                                        module.__version__,
                                                                        version)
        if prefs.core.outdated_dependency_error:
            raise ImportError(message)
        else:

            logger.warn(message, 'outdated_dependency')

for name, version in [('numpy', '1.8.0'),
                      ('scipy', '0.13.3'),
                      ('sympy', '0.7.6')]:
    _check_dependency_version(name, version)

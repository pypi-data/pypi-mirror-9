"""preprocessors packages"""

__docformat__ = "restructuredtext en"

try:
    import apycotlib
except ImportError: # allow to run from sources
    from cubes.apycot import _apycotlib as apycotlib
    import sys
    sys.modules['apycotlib'] = apycotlib

from apycotlib import ApycotObject

class BasePreProcessor(ApycotObject):
    """an abstract class providing some common utilities for preprocessors
    """
    __type__ = 'preprocessor'

    def run(self, test, path):
        """Run preprocessor against source in <path> in <test> context"""
        raise NotImplementedError()

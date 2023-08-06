"""__init__ module for pygeprocessing, imports all the geoprocessing functions
    into the pygeoprocessing namespace"""

import unittest
import logging
import os

from pygeoprocessing.geoprocessing import *

LOGGER = logging.getLogger('pygeoprocessing')
LOGGER.setLevel(logging.DEBUG)

def test():
    """run modulewide tests"""
    LOGGER.info('running tests on %s', os.path.dirname(__file__))
    suite = unittest.TestLoader().discover(os.path.dirname(__file__))
    unittest.TextTestRunner(verbosity=2).run(suite)
__version__ = "0.1.0.dev71"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.1.1'
build_id = 'release/0.1.1-da52006c2376'
py_arch = '32bit'
release = '0.1.0'
version_str = 'release/0.1.1-da52006c2376'

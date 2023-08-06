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
__version__ = "0.1.8.dev9"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'feature/nodata_byte_raster_refactor'
build_id = 'feature/nodata_byte_raster_refactor-17a33cd54dff'
py_arch = '32bit'
release = '0.1.8'
version_str = 'feature/nodata_byte_raster_refactor-17a33cd54dff'
__version__ = "0.1.8.dev10"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'feature/nodata_byte_raster_refactor'
build_id = 'feature/nodata_byte_raster_refactor-e6432994ae7b'
py_arch = '32bit'
release = '0.1.8'
version_str = 'feature/nodata_byte_raster_refactor-e6432994ae7b'
__version__ = "0.1.8.dev10"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'feature/nodata_byte_raster_refactor'
build_id = 'feature/nodata_byte_raster_refactor-e6432994ae7b'
py_arch = '32bit'
release = '0.1.8'
version_str = 'feature/nodata_byte_raster_refactor-e6432994ae7b'
__version__ = "0.1.8.dev10"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'feature/nodata_byte_raster_refactor'
build_id = 'feature/nodata_byte_raster_refactor-e6432994ae7b'
py_arch = '32bit'
release = '0.1.8'
version_str = 'feature/nodata_byte_raster_refactor-e6432994ae7b'
__version__ = "0.1.8.dev14"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.2.0'
build_id = 'release/0.2.0-ff2c7d67e105'
py_arch = '32bit'
release = '0.1.8'
version_str = 'release/0.2.0-ff2c7d67e105'
__version__ = "0.1.8.dev14"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.2.0'
build_id = 'release/0.2.0-ff2c7d67e105'
py_arch = '32bit'
release = '0.1.8'
version_str = 'release/0.2.0-ff2c7d67e105'
__version__ = "0.1.8.dev14"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.2.0'
build_id = 'release/0.2.0-ff2c7d67e105'
py_arch = '32bit'
release = '0.1.8'
version_str = 'release/0.2.0-ff2c7d67e105'
__version__ = "0.1.8.dev14"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.2.0'
build_id = 'release/0.2.0-ff2c7d67e105'
py_arch = '32bit'
release = '0.1.8'
version_str = 'release/0.2.0-ff2c7d67e105'
__version__ = "0.1.8.dev17"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.2.0'
build_id = 'release/0.2.0-5f4f55c53757'
py_arch = '32bit'
release = '0.1.8'
version_str = 'release/0.2.0-5f4f55c53757'
__version__ = "0.1.8.dev17"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.2.0'
build_id = 'release/0.2.0-5f4f55c53757'
py_arch = '32bit'
release = '0.1.8'
version_str = 'release/0.2.0-5f4f55c53757'
__version__ = "0.2.0"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'master'
build_id = 'master-8faef955bc0b'
py_arch = '32bit'
release = '0.2.0'
version_str = '0.2.0'
__version__ = "0.2.0"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'master'
build_id = 'master-8faef955bc0b'
py_arch = '32bit'
release = '0.2.0'
version_str = '0.2.0'

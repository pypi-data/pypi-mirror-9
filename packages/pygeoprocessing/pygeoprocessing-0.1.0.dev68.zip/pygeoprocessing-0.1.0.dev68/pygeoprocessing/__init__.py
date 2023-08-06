"""__init__ module for pygeprocessing, imports all the geoprocessing functions
	into the pygeoprocessing namespace"""

import logging
LOGGER = logging.getLogger('pygeoprocessing')
LOGGER.setLevel(logging.ERROR)

from pygeoprocessing.geoprocessing import *
__version__ = "0.1.0.dev68"
build_data = ['release', 'build_id', 'py_arch', 'branch', 'version_str']
branch = 'release/0.1.1'
build_id = 'release/0.1.1-559732be923d'
py_arch = '32bit'
release = '0.1.0'
version_str = 'release/0.1.1-559732be923d'

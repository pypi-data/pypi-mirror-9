__author__ = 'platinummonkey'

import os

__rexpro_version_path__ = os.path.realpath(__file__ + '/../VERSION')
__version__ = open(__rexpro_version_path__, 'r').readline().strip()

from rexpro.connection import RexProConnection, RexProConnectionPool

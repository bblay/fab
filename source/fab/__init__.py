##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################
"""
Flexible build system for scientific software.
"""

import logging

logging.getLogger('fab').setLevel(logging.INFO)

__version__ = '2020.4.dev0'


class FabException(Exception):
    pass

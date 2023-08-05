# coding=utf-8
# Filename: logger.py
# pylint: disable=locally-disabled,C0103
"""
The logging facility.

"""
from __future__ import division, absolute_import, print_function

__author__ = 'tamasgal'

import logging
import logging.config
try:
    logging.config.fileConfig('logging.conf')
except Exception:
    logging.basicConfig()

logging.addLevelName(logging.INFO, "\033[1;32m%s\033[1;0m" %
                     logging.getLevelName(logging.INFO))
logging.addLevelName(logging.DEBUG, "\033[1;34m%s\033[1;0m" %
                     logging.getLevelName(logging.DEBUG))
logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" %
                     logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" %
                     logging.getLevelName(logging.ERROR))

# pylint: disable=C0103
formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')




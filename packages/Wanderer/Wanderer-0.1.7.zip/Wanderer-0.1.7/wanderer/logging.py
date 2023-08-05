# -*- coding: utf-8 -*-
'''
logging
=======
Wanderer logging setting
'''

from __future__ import absolute_import
import logging
from logging import getLogger, StreamHandler, FileHandler, Formatter
import os


STANDARD_FORMAT = '\n<%(asctime)s>[%(levelname)s %(module)s] %(message)s'
DEBUG_FORMAT = (
    '\n<%(asctime)s>[%(levelname)s %(module)s](%(funcName)s %(lineno)d)\n'
    '%(message)s\n'
)


def new_logger(app):
    '''Create a new logger for a Wanderer instance.

    :param app: Wanderer instance'''

    sh = StreamHandler()
    if app.config.debug:
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(Formatter(DEBUG_FORMAT))
    else:
        sh.setFormatter(Formatter(STANDARD_FORMAT))

    logger = getLogger(os.path.basename(app.root))
    logger.addHandler(sh)

    return logger

# -*- coding: utf-8 -*-
"""
:summary: All logging related functionality is done in here.

:author: francis.horsman@gmail.com
"""

import os
from logging import DEBUG, ERROR, basicConfig
from logging import getLogger as Logger

from .defaults import DEFAULT_LOGGING_FORMAT, DEFAULT_LOGFILE


def get_logger(name, *args, **kwargs):
    return Logger(name, *args, **kwargs)


def setup_logging(logger, profile, format=DEFAULT_LOGGING_FORMAT):
    if profile.logging.verbose:
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(ERROR)
    # Set the file handler and default config
    basicConfig(format=format,
                filename=os.path.join(os.getcwd(), DEFAULT_LOGFILE),
                filemode='w')
    # TODO: Set up file handler, other handlers etc.
    pass


if __name__ == '__main__':  # pragma no cover
    pass

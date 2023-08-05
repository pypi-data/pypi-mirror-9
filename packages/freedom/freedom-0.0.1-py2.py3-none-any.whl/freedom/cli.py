# -*- coding: utf-8 -*-
"""
:summary: The command-line invoked wrapper for the release system.

:author: francis.horsman@gmail.com
"""

from logging import getLogger

from .core import releaser


class cli(object):
    def __init__(self, **kwargs):
        """
        class constructor.

        :param kwargs: see ..release.py
        """
        self.logger = getLogger('releaser-cli')
        self.kwargs = kwargs

    def __call__(self):
        return self.execute()

    def execute(self, logger=None, kwargs=None):
        logger = logger or self.logger
        kwargs = kwargs or self.kwargs
        return releaser(run=True, logger=logger, **kwargs)


if __name__ == '__main__':  # pragma no cover
    pass

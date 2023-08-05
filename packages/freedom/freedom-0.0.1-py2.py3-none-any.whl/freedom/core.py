# -*- coding: utf-8 -*-
"""
:summary: The Release process work-flow management.

:author: francis.horsman@gmail.com
"""

import collections
from datetime import datetime as dt

from .actions import Actions
from .builder import Builder
from .export import Exporter
from .history import History
from .logger import get_logger, setup_logging
from .profiles import NewProfile
from .publish import Publisher
from .task import Task
from .utils import get_env_str
from .vcs import Git


class releaser(object):
    """
    The releaser's work-flow.
    """

    def __init__(self, run=False, logger=None, **kwargs):
        self.logger = logger or get_logger('releaser')

        self.profile = self._compile_profile(kwargs)
        setup_logging(self.logger, profile=self.profile)

        self.logger.debug('Release commencing @ %s' % dt.utcnow().isoformat())
        self.logger.debug(self._dump_args())
        self.logger.debug('working directory: %s' % self.profile.vcs.git_repo)
        self.logger.info('primary env: %s' % get_env_str())

        self.task = Task(self.profile, logger=self.logger)
        if self.task.finished:
            self.logger.warn(
                'No actions to perform, Finished release processing.')
            return

        # Create helpers:
        self.exporter = Exporter(self.profile, logger=self.logger)
        self.git = Git(self.profile, logger=self.logger)
        self.history = History(self.profile, self.git, logger=self.logger)
        self.builder = Builder(self.profile, logger=self.logger)
        self.publisher = Publisher(self.profile, self.builder,
                                   logger=self.logger)
        self.actions = Actions(self.profile, self.history, self.publisher,
                               self.git, self.builder, logger=self.logger)
        self.task.set_actions(self.actions)

        self.logger.debug(str(self.exporter))
        self.logger.info('env: %s' % get_env_str())

        if run is True:
            self()

    def _dump_args(self):
        s = ['Args:']
        s.append(unicode(self.profile.dump))
        return '\n'.join(s)

    @staticmethod
    def _compile_profile(kwargs):
        return NewProfile.build(**kwargs)

    def __call__(self):
        self.logger.warn('Starting release processing')
        try:
            collections.deque(self.task.run(), maxlen=0)
        finally:
            self.logger.warn('Finished release processing.')


if __name__ == '__main__':  # pragma no cover
    pass

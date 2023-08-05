# -*- coding: utf-8 -*-
"""
:summary: All publishing to pypi is done from here.

:author: francis.horsman@gmail.com
"""

from .logger import get_logger


class Publisher(object):
    def __init__(self, profile, builder, logger=None, **kwargs):
        self.logger = logger or get_logger('publisher')
        self.kwargs = kwargs
        self.profile = profile
        self.builder = builder

    def pypi(self, new_version):
        self.logger.info('Publishing %s to pypi' % new_version)
        if not self.profile.dry_run:
            return self.builder.build_release(new_version, upload=True)
        else:
            self.logger.info('simulated publish_release.')


if __name__ == '__main__':  # pragma no cover
    pass

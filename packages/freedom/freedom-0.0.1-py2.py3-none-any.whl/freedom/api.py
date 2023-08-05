# -*- coding: utf-8 -*-

"""
A simple helper interface to the more complex releaser.
"""

from logging import getLogger
import copy

from .core import releaser
from .utils import update_dict

api_logger = getLogger('api')


def _exec(run, logger, actions, **args):
    logger = logger or api_logger
    kwargs = update_dict(actions, copy.deepcopy(args))
    if not kwargs.get('git_repo', None):
        raise ValueError('git_repo must be specified.')

    releaser(run=run, logger=logger, **kwargs)
    if run:
        releaser()
    else:
        return releaser


def publish(run=False, logger=None, **args):
    """
    The full-monty: tag, push_release and publish_release.

    :param run: Immediately run the release, False - return an object on which
        can be called with no arguments.
    :param logger: logger to use.
    :param args: kwargs to pass to the releaser constructor.
    """
    _exec(run, logger, dict(tag=True, push=True, publish=True), **args)


def push(run=False, logger=None, **args):
    _exec(run, logger, dict(tag=False, push=True, publish=False, build=False),
          **args)


def tag(run=False, logger=None, **args):
    _exec(run, logger, dict(tag=True, push=False, publish=False, build=False),
          **args)


def build(run=False, logger=None, **args):
    _exec(run, logger, dict(tag=False, push=False, publish=False, build=True),
          **args)


if __name__ == '__main__':  # pragma no cover
    pass

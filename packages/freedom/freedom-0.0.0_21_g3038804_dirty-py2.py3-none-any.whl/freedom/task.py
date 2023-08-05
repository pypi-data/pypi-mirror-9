# -*- coding: utf-8 -*-
"""
:summary: All task related activity in here.

:author: francis.horsman@gmail.com
"""

from abc import ABCMeta
import collections
from functools import wraps
import traceback

import six

from .errors import TaskConfigurationError
from .logger import get_logger


class _TaskError(Exception):
    pass


class _TaskContext(dict):
    """
    Holds details of 'stuff' for passing between tasks.
    """
    pass


class TaskNotRequired(Exception):
    pass


_SUPPORTED_TASKS = collections.defaultdict(list)


def build_action(action):
    @wraps(build_action)
    def _actioner(self, context, **kwargs):
        func = getattr(self._parent.actions, action)
        return func(context)

    return _actioner


class TaskRegistry(type):
    def __new__(mcs, name, bases, dct):
        if name != '_Task':
            action = dct.get('ACTION', None)
            profile = dct.get('PROFILE', None)
            phase = dct.get('PHASE', None)
            if not bases == (object,):
                for what, attribute, e_type in [(action, 'ACTION', basestring),
                                                (
                                                        profile, 'PROFILE',
                                                        basestring),
                                                (phase, 'PHASE', int)]:
                    if not what or not isinstance(what, e_type):
                        raise TaskConfigurationError(
                            '%s is not configured correctly, it must specify a'
                            '%s class attribute of type %s' % (
                                what, attribute, e_type))
            dct['_action'] = build_action(action)
            del dct['PHASE']
            del dct['ACTION']
        cls = super(TaskRegistry, mcs).__new__(mcs, name, bases, dct)
        if name != '_Task':
            _SUPPORTED_TASKS[phase].append(cls)
        return cls


@six.add_metaclass(TaskRegistry)
@six.add_metaclass(ABCMeta)
class _Task(object):
    """
    Holds details of an individual task (action).

    The exact mechanics of how tasks work and how they pass data between
        themselves is T.B.D.
    """

    def __init__(self, parent):
        self._parent = parent  # parent Task instance.
        self._check_is_required(parent.profile)

    @classmethod
    def _check_is_required(cls, profile):
        what = profile
        for token in cls.PROFILE.split('.'):
            what = getattr(what, token, None)
            if not what:
                raise TaskNotRequired()

    @property
    def impl(self):
        return self._parent.actions

    def __call__(self, context):
        """
        Perform the action related to this task.

        :param context: dict - update in-place as you see fit.
        :return: The result from the action, T.B.D.
        """
        return self._action(context)


class _TaskBuildDocs(_Task):
    PHASE = 1
    ACTION = 'build_release_docs'
    PROFILE = 'build.build_docs'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.build_release_docs


class _TaskBuildTest(_Task):
    PHASE = 1
    ACTION = 'build_test'
    PROFILE = 'build.build_test'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.build_test


class _TaskBuildRelease(_Task):
    PHASE = 1
    ACTION = 'build_release'
    PROFILE = 'build.build.build_release'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.build_release


class _TaskTagRelease(_Task):
    PHASE = 2
    ACTION = 'tag_release'
    PROFILE = 'vcs.tag_release'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.tag_release


class _TaskPushRelease(_Task):
    PHASE = 2
    ACTION = 'push_release'
    PROFILE = 'vcs.push_release'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.push_release


class _TaskPublishPypi(_Task):
    PHASE = 3
    ACTION = 'publish_release'
    PROFILE = 'publish.publish_pypi'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.publish_release


class _TaskPublishDocsPypi(_Task):
    PHASE = 3
    ACTION = 'publish_release_docs_pypi'
    PROFILE = 'publish.publish_docs_pypi'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.publish_release_docs_pypi


class _TaskPublishDocsRtd(_Task):
    PHASE = 3
    ACTION = 'publish_release_docs_rtd'
    PROFILE = 'publish.publish_docs_rtd'

    # def __init__(self, parent):
    # _Task.__init__(self, parent)
    # self._action = self.impl.publish_release_docs_rtd


class Task(object):
    def __init__(self, profile, logger=None):
        self.profile = profile
        self.actions = None
        self.logger = logger or get_logger('Tasks')
        self._context = self._create_context
        self._tasks = self._init()
        self._finished = True if not self._tasks else False

    @property
    def _create_context(self):
        return _TaskContext(version=None)

    def set_actions(self, actions):
        self.actions = actions if actions else []

    def _init(self):
        result = []
        for phase, tasks in sorted(_SUPPORTED_TASKS.items()):
            self.logger.debug('Building phase %d tasks' % phase)
            for task in tasks:
                try:
                    impl = task(self)
                except TaskNotRequired:
                    self.logger.debug('Task not required: %s' % task)
                else:
                    self.logger.debug('Task required: %s' % task)
                    result.append(impl)
        return result

    @property
    def finished(self):
        return self._finished is True

    def run(self):
        """
        Iterate within this run method so as to keep the state of the iteration
        within this class instance.
        """
        self.logger.warn('Starting task processing')
        try:
            for _ in self:
                yield
        except Exception as err:
            # If one task fails, we fail completely:
            self.logger.error('\n'.join([err.message, traceback.format_exc()]))
        finally:
            self._finished = True
            self.logger.warn('Finished task processing.')

    def __iter__(self):
        """
        Work all the tasks ( the order has already been determined during
            _init() ).
        Lets deal with the release flow first, then take care of docs, etc
            after.
        """
        for index, task in enumerate(self._tasks):
            self.logger.debug('Working task %d: %s' % (index, str(task)))
            yield task(self._context)


if __name__ == '__main__':  # pragma no cover
    pass

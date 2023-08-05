# -*- coding: utf-8 -*-
"""
:summary: All vcs operations are done through here.

:author: francis.horsman@gmail.com
"""

# from git import *
#
#
# class Git(object):
# """
# This class performs all git command handling.
# """
#
# def __init__(self, **kwargs):
# try:
# path = kwargs['git_repo']
# except:
# raise ValueError('git repo path not specified!')
# self.repo = Repo(path)
# self.config_writer = self.repo.config_writer()
#
# def add(self, push_all=False, comment=None):
# s = ['push_release']
# if push_all is True:
# s.append('-a')
# if comment is not None:
# s.append('-m')
# s.append(comment)
# return self.git(*tuple(s))
#
# def tag(self, name, comment=None):
# if comment is not None:
# return self.repo.tag(name, comment)
# return self.repo.tag(name)
#
# def push_release(self, push_all=False, push_tags=False):
# if push_all and push_tags:
# raise ValueError('push_all and push_tags are mutually exclusive !')
# if push_all:
# print('Pushing ALL to git')
# self.git('push_release', '--all')
# if push_tags:
# print('Pushing TAGS to git')
# self.git('push_release', '--tags')
# if not push_all and not push_tags:
# self.git('push_release')

from sh import git as GIT

from .logger import get_logger


class Git(object):
    def __init__(self, profile, logger=None):
        self.logger = logger or get_logger('git')
        self.profile = profile

        if not self.profile.vcs.git_repo:
            # Should be taken care of in the args parsing already!
            raise ValueError('git repo path not specified!')

        # Now check the status of the repo (fail-fast):
        self.status()

    def _exec(self, command):
        if not self.profile.misc.dry_run:
            self.logger.info('git.%s' % command)
            return GIT(*tuple(command), _cwd=self.profile.vcs.git_repo)
        else:
            self.logger.info('simulated git.%s' % command)

    def status(self):
        return self._exec(['status'])

    @property
    def tags(self):
        return self._exec(['tag']) or []

    @property
    def current_tag(self):
        return self.tags[-1:]

    def add(self, add_all=False, comment=None):
        s = ['add']
        if add_all is True:
            s.append('-a')
        if comment is not None:
            s.append('-m')
            s.append(comment)
        return self._exec(s)

    def tag(self, tag_name, comment=None):
        s = list('tag', tag_name)
        if comment is not None:
            s.append('-m')
            s.append(comment)
        return self._exec(s)

    def push(self, push_all=False, push_tags=False):
        if push_all:
            self._push(True, False)
        if push_tags:
            self._push(False, True)

    def _push(self, push_all, push_tags):
        s = ['push_release']
        if push_all and push_tags:
            raise Exception('push_all and push_tags are mutually exclusive')
        elif push_all:
            self.logger.info('Pushing ALL to git')
            s.append('--all')
        elif push_tags:
            self.logger.info('Pushing TAGS to git')
            s.append('--tags')
        else:
            self.logger.info('Pushing to git')
        self._exec(s)

    def __str__(self):
        return 'GitRepo(%s)' % self.profile.vcs.git_repo


if __name__ == '__main__':  # pragma no cover
    pass

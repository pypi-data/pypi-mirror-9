# -*- coding: utf-8 -*-
"""
:summary: All building related activities in here.

:author: francis.horsman@gmail.com
"""

from logging import getLogger

from sh import python

from .utils import new_env, get_env_str


class Builder(object):
    def __init__(self, profile, logger=None):
        self.profile = profile
        self.logger = logger or getLogger('builder')

    def _exec(self, *args, **kwargs):
        cwd = kwargs.get('cwd', None)
        env = kwargs.get('env', None)
        cwd = self.profile.vcs.git_repo if cwd is None else cwd
        env = env if env is not None else self._get_env()

        self.logger.debug('building with cwd: %s' % cwd)
        self.logger.debug('building with env: %s' % get_env_str(env))

        if self.profile.misc.dry_run:
            self.logger.debug('simulated build_release.%s' % list(args))
        else:
            return python(*args, _cwd=cwd, _env=env)

    def _get_env(self, d=None):
        d = {} if d is None else d
        d.update(dict(HOME=self.profile.build.home))
        return new_env(d)

    def _build_release(self, version):
        self.logger.info('Building: %s' % version)
        return self._exec('setup.py', 'build_release', 'sdist', 'bdist_egg')

    def _build_and_upload_release(self, version):
        self.logger.info('Building and uploading: %s' % version)
        return self._exec('setup.py', 'build_release', 'sdist', 'bdist_egg',
                          'upload')

    def _upload_release(self, version):
        self.logger.info('Building and uploading: %s' % version)
        return self._exec('setup.py', 'build_release', 'sdist', 'bdist_egg',
                          'upload')

    def build_release(self, version, upload=False):
        return self._build_and_upload_release(
            version) if upload else self._build_release(
            version)

    def build_test(self, *args, **kwargs):
        cwd = kwargs.get('cwd', None)
        env = kwargs.get('env', None)
        cwd = self.profile.vcs.git_repo if cwd is None else cwd
        env = env if env is not None else self._get_env()

        self.logger.debug('testing with cwd: %s' % cwd)
        self.logger.debug('testing with env: %s' % get_env_str(env))

        if self.profile.misc.dry_run:
            self.logger.debug('simulated build_release.%s' % list(args))
        else:
            runtests(_cwd=cwd, _env=env)

    def build_release_docs(self):
        self.logger.info('Building release docs')
        return self._exec('setup.py', 'build_sphinx')

    def upload_release_docs_pypi(self):
        self.logger.info('Uploading release docs to pypi')
        return self._exec('setup.py', 'upload_sphinx')

    def build_and_publish_release_docs_pypi(self):
        self.build_release_docs()
        self.upload_release_docs_pypi()

    def build_and_publish_release_docs_rtd(self):
        self.build_release_docs()
        raise NotImplementedError


if __name__ == '__main__':  # pragma no cover
    pass

# -*- coding: utf-8 -*-
"""
:summary: All historian related activity is done from here.

:author: francis.horsman@gmail.com
"""

from datetime import datetime as dt

from sh import python

from .logger import get_logger
from .defaults import DEFAULT_HISTORY_COMMENT


class AllHistory(object):
    def __init__(self, lines, meta, delimiter):
        self.comments = []
        self.lines = self._strip_meta(lines, delimiter)
        self.meta = meta

    def add(self, new_version, comment, date=None):
        if date is None:
            date = dt.utcnow().strftime('%Y-%m-%d')
        self.comments.insert(0, self._new_comment(comment or '', date,
                                                  new_version))

    @staticmethod
    def _new_comment(comment, date, new_version):
        return DEFAULT_HISTORY_COMMENT % (new_version, date, comment or '')

    @staticmethod
    def _strip_meta(lines, delimiter):
        for index, line in enumerate(lines):
            if delimiter in line:
                return lines[index + 1:]
        return lines

    def write(self, filename):
        lines = self.meta + self.comments + self.lines
        history = ''.join(lines)
        open(filename, 'w').write(history)


class History(object):
    """
    All functionality relating to historian and versions.
    """

    def __init__(self, profile, git, logger=None):
        assert git
        self.git = git
        self.profile = profile
        self.logger = logger or get_logger('historian')
        self._current_version = None

    @property
    def current_version(self):
        if self._current_version is None:
            self._current_version = self._get_current_version_from_vcs()
        return self._current_version

    @staticmethod
    def generate_new_version(history_version_overwrite, current_version):
        """
        Increment the current version.

        :param history_version_overwrite: new version to use irrespective of
            current version.
        :param current_version: Existing 'major.minor.revision', eg: '0.1.2'
        :return: Incremented 'major.minor.revision', eg: '0.1.3'
        """
        tokens = current_version.split('.')
        if history_version_overwrite:
            tokens_overwrite = history_version_overwrite.split('.')
            if tokens_overwrite < tokens:
                raise ValueError(
                    'attempt to create new version which is <= '
                    'than the current version!')
            tokens = tokens_overwrite
        else:
            tokens[2] = str(int(tokens[2]) + 1)
        return '.'.join(tokens)

    def _exec(self, args):
        if not self.profile.misc.dry_run:
            return python(*args, _cwd=self.profile.vcs.git_repo)
        else:
            self.logger.info('simulated python.%s' % args)

    def _get_current_version_from_vcs(self):
        current_version = self.git.current_tag or '0.0.1'
        # current_version = self._exec(['setup.py', '--version']).split('-')[
        # 0] or '0.0.1'
        self.logger.debug('Current tagged version: %s' % current_version)
        return current_version

    def commit_history(self, history_file):
        self.logger.info('Adding historian file: %s to git' % history_file)
        self.git.add(history_file)
        self.git.commit(push_all=True, comment='Updating tag and historian')

    def read_history(self, history_file):
        self.logger.debug('Reading historian file: %s' % history_file)
        return open(history_file).readlines()

    def rewrite_history(self, new_version, history_file, comment, date, meta,
                        delimiter):
        self.logger.info('Rewriting historian: %s' % new_version)
        h = AllHistory(self.read_history(history_file), meta, delimiter)
        h.add(new_version, comment, date=date)
        h.write(history_file)
        self.commit_history(history_file)

    def set_current_version(self, new_version, msg='updating changelog'):
        self.logger.info('Tagging with new version: %s' % new_version)
        try:
            return self.git.tag_release(new_version, comment=msg)
        finally:
            if not self.profile.misc.dry_run:
                # Force a reload of the current_version if tagging fails:
                self._current_version = None


if __name__ == '__main__':  # pragma no cover
    pass

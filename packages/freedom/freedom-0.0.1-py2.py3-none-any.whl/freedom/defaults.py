# -*- coding: utf-8 -*-
"""
:summary: Sensible project defaults

:author: francis.horsman@gmail.com
"""

import os


class ExportFormat(object):
    JSON = 'json'
    PICKLE = 'pickle'
    YAML = 'yaml'
    MSGPACK = 'msgpack'


DEFAULT_CWD = os.getcwd()
DEFAULT_BUILD_TEST = False
DEFAULT_EXPORT_OPTIONS = None
DEFAULT_EXPORT_FORMAT = ExportFormat.YAML
DEFAULT_DRYRUN = True
DEFAULT_LOGGING_FORMAT = '%(levelname)-8s %(asctime)-15s  %(message)s'
DEFAULT_LOGFILE = '.log'
DEFAULT_VERBOSE = True
DEFAULT_ENV = 'RELEASEME_PROFILE'
DEFAULT_TAG_RELEASE = False
DEFAULT_BUILD_RELEASE = False
DEFAULT_BUILD_RELEASE_DOCS = False
DEFAULT_PUBLISH_PYPI = False
DEFAULT_PUBLISH_DOCS_PYPI = False
DEFAULT_PUBLISH_DOCS_RTD = False
DEFAULT_PUSH_RELEASE = False
DEFAULT_PROFILE = '~/.releaserc'
DEFAULT_PYPIRC = os.path.join(os.path.realpath(os.environ.get('HOME', '~')),
                              '.pypirc')
DEFAULT_GIT_PROFILE = '~/.gitrc'
DEFAULT_GIT_REPO = DEFAULT_CWD
DEFAULT_HISTORY_FILE = 'HISTORY.rst'
DEFAULT_HISTORY_DATE = None
DEFAULT_HISTORY_VERSION = None
DEFAULT_HISTORY_DELIMITER = '========='
DEFAULT_HISTORY_META = """.. :changelog:

Changelog
%s

""" % DEFAULT_HISTORY_DELIMITER

DEFAULT_HISTORY_COMMENT = """%s %s
----------------
* %s
"""


class OptionsKey(object):
    VERBOSE = 'verbose'
    BUILD_TEST = 'test'
    DRYRUN = 'dryrun'
    PYPIRC = 'pypirc'
    EXPORT_OPTIONS = 'generate-rcfile'
    TAG_RELEASE = 'tag-release'
    PUSH_RELEASE = 'push-release'
    BUILD_RELEASE = 'build-release'
    BUILD_RELEASE_DOCS = 'build-release-docs'
    PUBLISH_RELEASE_PYPI = 'publish-release-pypi'
    PUBLISH_RELEASE_DOCS_PYPI = 'publish-release-docs-pypi'
    PUBLISH_RELEASE_DOCS_RTD = 'publish-release-docs-rtd'
    PROFILE_ENV = 'profile-env'
    PROFILE = 'profile'
    HISTORY_VERSION = 'history-version'
    HISTORY_DATE = 'history-date'
    HISTORY_COMMENT = 'history-comment'
    HISTORY_FILE = 'history-file'
    HISTORY_DELIMITER = 'history-delimiter'
    HISTORY_META = 'history-meta'
    GIT_REPO = 'git-repo'
    GIT_PROFILE = 'git-profile'


def get_opts_key(key):
    return key.replace('-', '_')


def get_opt(key):
    return ''.join(['--', key])


if __name__ == '__main__':  # pragma no cover
    pass

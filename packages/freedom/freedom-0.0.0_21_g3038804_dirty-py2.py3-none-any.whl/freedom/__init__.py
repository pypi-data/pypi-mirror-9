# -*- coding: utf-8 -*-
# flake8: noqa

__author__ = 'Francis Horsman'
__url__ = 'https://bitbucket.org/sys-git/releaseme'
__email__ = 'francis.horsman@gmail.com'
__short_description__ = 'A pure-python git and pypi release management tool'
__copyright__ = u'2015, Francis Horsman'

from .api import publish, push, tag, build
from .core import releaser
from .errors import ProfileLoadError, NoProfileFile
from .version import get_versions

__version__ = get_versions()['version']
del get_versions

if __name__ == '__main__':  # pragma: no cover
    print(__short_description__)

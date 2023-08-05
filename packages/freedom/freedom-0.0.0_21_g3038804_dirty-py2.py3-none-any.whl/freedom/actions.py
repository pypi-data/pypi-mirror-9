# -*- coding: utf-8 -*-
"""
:summary: All actions related functionality goes in here.

:author: francis.horsman@gmail.com
"""

from .logger import get_logger


class Actions(object):
    """
    Actions are called by a Task only.

    :see: .task.py
    :attention: all public methods must have the same signature:
        "def method_name(self, context)".
    """

    def __init__(self, profile, history, publisher, git, builder, logger=None):
        self.profile = profile
        self.historian = history
        self.publisher = publisher
        self.git = git
        self.builder = builder
        self.logger = logger or get_logger('Actions')

    def tag_release(self, context):
        self.logger.info('Action: Tag-Release')
        history_version_overwrite = self.profile.history.history_file
        new_version = self.historian.generate_new_version(
            history_version_overwrite, self.historian.current_version)
        self.historian.rewrite_history(new_version, *self.profile.history)
        self.historian.set_current_version(new_version)

    def push_release(self, context):
        self.logger.info('Action: Push-Release')
        return self.git.push(push_all=True, push_tags=True)

    def publish_release(self, context):
        self.logger.info('Action: Publish-Release')
        version = context.get('version', None)
        if version is None:
            version = self.historian.current_version
        return self.publisher.pypi(version)

    def build_release(self, context):
        self.logger.info('Action: Build-Release')
        version = context.get('version', None)
        if version is None:
            version = self.historian.current_version
        return self.builder.build_release(version)

    def build_test(self, context):
        self.logger.info('Action: Build-Test')
        return self.builder.build_test()

    def build_release_docs(self, context):
        self.logger.info('Action: Build-Release-docs-pypi')
        return self.builder.build_release_docs()

    def build_and_publish_release_docs_pypi(self, context):
        self.logger.info('Action: Build-Publish-Release-docs-pypi')
        return self.builder.build_and_publish_release_docs_pypi()

    def build_and_publish_release_docs_rtd(self, context):
        self.logger.info('Action: Build-Publish-Release-docs-rtd')
        return self.builder.build_and_publish_release_docs_rtd()

    def publish_release_docs_pypi(self, context):
        self.logger.info('Action: Publish-Release-docs-pypi')
        return self.builder.publish_release_docs_pypi()

    def publish_release_docs_rtd(self, context):
        self.logger.info('Action: Publish-Release-docs-rtd')
        return self.builder.publish_release_docs_rtd()


if __name__ == '__main__':  # pragma no cover
    pass

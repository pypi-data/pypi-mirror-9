# -*- coding: utf-8 -*-
"""
:summary: All exceptions we export.

:author: francis.horsman@gmail.com
"""


class ProfileLoadError(Exception):
    """
    There was an error loading the profile
    """

    def __init__(self, exc, msg):
        super(ProfileLoadError, self).__init__(exc)
        self.load_error = msg


class NoProfileFile(Exception):
    """
    The profile file is not found at the given location.
    """
    pass


class UnknownExportCodec(Exception):
    """
    An export codec with the given name was not found.
    """

    def __init__(self, codec):
        Exception.__init__(self, codec)
        self.codec = codec

    def __str__(self):
        return 'Unknown codec: \'%s\'' % self.codec


class ExporterConfigurationError(Exception):
    """
    An error occurred in the exporter codec creation.
    """
    pass


class TaskConfigurationError(Exception):
    """
    An error occurred in the task creation.
    """
    pass


if __name__ == '__main__':  # pragma no cover
    pass

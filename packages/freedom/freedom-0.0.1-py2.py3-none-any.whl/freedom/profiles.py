# -*- coding: utf-8 -*-
"""
:summary: Profile and options handling.

:author: francis.horsman@gmail.com
"""

import os
import pprint

import yaml

from .defaults import DEFAULT_ENV, DEFAULT_VERBOSE, DEFAULT_DRYRUN, \
    DEFAULT_PUBLISH_DOCS_PYPI, DEFAULT_PUBLISH_DOCS_RTD, DEFAULT_PUBLISH_PYPI, \
    DEFAULT_GIT_REPO, DEFAULT_GIT_PROFILE, DEFAULT_BUILD_RELEASE, \
    DEFAULT_BUILD_RELEASE_DOCS, DEFAULT_TAG_RELEASE, DEFAULT_PUSH_RELEASE, \
    DEFAULT_PYPIRC, get_opts_key, OptionsKey, DEFAULT_HISTORY_FILE, \
    DEFAULT_HISTORY_DELIMITER, DEFAULT_HISTORY_DATE, DEFAULT_HISTORY_VERSION, \
    DEFAULT_HISTORY_META, DEFAULT_HISTORY_COMMENT, DEFAULT_EXPORT_OPTIONS, \
    DEFAULT_BUILD_TEST
from .errors import NoProfileFile, ProfileLoadError
from .utils import update_dict
from .export import iExporter


class HistorianProfile(dict):
    @staticmethod
    def get_args(**kwargs):
        return {
            get_opts_key(OptionsKey.HISTORY_FILE): kwargs.get(
                get_opts_key(OptionsKey.HISTORY_FILE),
                DEFAULT_HISTORY_FILE),
            get_opts_key(
                OptionsKey.HISTORY_COMMENT): kwargs.get(
                get_opts_key(OptionsKey.HISTORY_COMMENT),
                DEFAULT_HISTORY_COMMENT),
            get_opts_key(
                OptionsKey.HISTORY_DATE): kwargs.get(
                get_opts_key(OptionsKey.HISTORY_DATE),
                DEFAULT_HISTORY_DATE),
            get_opts_key(
                OptionsKey.HISTORY_META): kwargs.get(
                get_opts_key(OptionsKey.HISTORY_META),
                DEFAULT_HISTORY_META),
            get_opts_key(
                OptionsKey.HISTORY_DELIMITER): kwargs.get(
                get_opts_key(OptionsKey.HISTORY_DELIMITER),
                DEFAULT_HISTORY_DELIMITER),
            get_opts_key(
                OptionsKey.HISTORY_VERSION): kwargs.get(
                get_opts_key(OptionsKey.HISTORY_VERSION),
                DEFAULT_HISTORY_VERSION)}

    @property
    def history_file(self):
        return self.get(get_opts_key(OptionsKey.HISTORY_FILE),
                        DEFAULT_HISTORY_FILE)

    @property
    def history_version(self):
        return self.get(get_opts_key(OptionsKey.HISTORY_VERSION),
                        DEFAULT_HISTORY_VERSION)

    @property
    def history_delimiter(self):
        return self.get(get_opts_key(OptionsKey.HISTORY_DELIMITER),
                        DEFAULT_HISTORY_DELIMITER)

    @property
    def history_date(self):
        return self.get(get_opts_key(OptionsKey.HISTORY_DATE),
                        DEFAULT_HISTORY_DATE)

    @property
    def history_meta(self):
        return self.get(get_opts_key(OptionsKey.HISTORY_META),
                        DEFAULT_HISTORY_META)

    @property
    def history_comment(self):
        return self.get(get_opts_key(OptionsKey.HISTORY_COMMENT),
                        DEFAULT_HISTORY_COMMENT)


class PublisherProfile(dict):
    @staticmethod
    def get_args(**kwargs):
        return {get_opts_key(OptionsKey.PUBLISH_RELEASE_DOCS_PYPI): kwargs.get(
            get_opts_key(OptionsKey.PUBLISH_RELEASE_DOCS_PYPI),
            DEFAULT_PUBLISH_DOCS_PYPI),
                get_opts_key(OptionsKey.PUBLISH_RELEASE_DOCS_RTD): kwargs.get(
                    get_opts_key(OptionsKey.PUBLISH_RELEASE_DOCS_RTD),
                    DEFAULT_PUBLISH_DOCS_RTD),
                get_opts_key(OptionsKey.PUBLISH_RELEASE_PYPI): kwargs.get(
                    get_opts_key(OptionsKey.PUBLISH_RELEASE_PYPI),
                    DEFAULT_PUBLISH_PYPI)}

    @property
    def publish_docs_pypi(self):
        return self.get(get_opts_key(OptionsKey.PUBLISH_RELEASE_DOCS_PYPI),
                        DEFAULT_PUBLISH_DOCS_PYPI)

    @property
    def publish_docs_rtd(self):
        return self.get(get_opts_key(OptionsKey.PUBLISH_RELEASE_DOCS_RTD),
                        DEFAULT_PUBLISH_DOCS_RTD)

    @property
    def publish_pypi(self):
        return self.get(get_opts_key(OptionsKey.PUBLISH_RELEASE_PYPI),
                        DEFAULT_PUBLISH_PYPI)


class BuilderProfile(dict):
    @staticmethod
    def get_args(**kwargs):
        return {
            get_opts_key(OptionsKey.BUILD_RELEASE_DOCS): kwargs.get(
                get_opts_key(OptionsKey.BUILD_RELEASE_DOCS),
                DEFAULT_BUILD_RELEASE_DOCS),
            get_opts_key(OptionsKey.BUILD_RELEASE): kwargs.get(
                get_opts_key(OptionsKey.BUILD_RELEASE),
                DEFAULT_BUILD_RELEASE),
            get_opts_key(OptionsKey.BUILD_TEST): kwargs.get(
                get_opts_key(OptionsKey.BUILD_TEST),
                DEFAULT_BUILD_TEST),
            get_opts_key(OptionsKey.PYPIRC): kwargs.get(
                get_opts_key(OptionsKey.PYPIRC), DEFAULT_PYPIRC)}

    @property
    def build_release(self):
        return self.get(get_opts_key(OptionsKey.BUILD_RELEASE),
                        DEFAULT_BUILD_RELEASE)

    @property
    def build_test(self):
        return self.get(get_opts_key(OptionsKey.BUILD_TEST),
                        DEFAULT_BUILD_TEST)

    @property
    def build_docs(self):
        return self.get(get_opts_key(OptionsKey.BUILD_RELEASE_DOCS),
                        DEFAULT_BUILD_RELEASE_DOCS)

    @property
    def pypirc(self):
        return self.get(get_opts_key(OptionsKey.PYPIRC), DEFAULT_PYPIRC)

    @property
    def home(self):
        return os.path.dirname(os.path.realpath(self.pypirc))


class VcsProfile(dict):
    @staticmethod
    def get_args(**kwargs):
        return {get_opts_key(OptionsKey.GIT_PROFILE): kwargs.get(
            get_opts_key(OptionsKey.GIT_PROFILE),
            DEFAULT_GIT_PROFILE),
                get_opts_key(OptionsKey.GIT_REPO): kwargs.get(
                    get_opts_key(OptionsKey.GIT_REPO),
                    DEFAULT_GIT_REPO),
                get_opts_key(OptionsKey.TAG_RELEASE): kwargs.get(
                    get_opts_key(OptionsKey.TAG_RELEASE),
                    DEFAULT_TAG_RELEASE),
                get_opts_key(OptionsKey.PUSH_RELEASE): kwargs.get(
                    get_opts_key(OptionsKey.PUSH_RELEASE),
                    DEFAULT_PUSH_RELEASE)}

    @property
    def git_repo(self):
        return self.get(get_opts_key(OptionsKey.GIT_REPO), DEFAULT_GIT_REPO)

    @property
    def git_profile(self):
        return self.get(get_opts_key(OptionsKey.GIT_PROFILE),
                        DEFAULT_GIT_PROFILE)

    @property
    def tag_release(self):
        return self.get(get_opts_key(OptionsKey.TAG_RELEASE),
                        DEFAULT_TAG_RELEASE)

    @property
    def push_release(self):
        return self.get(get_opts_key(OptionsKey.PUSH_RELEASE),
                        DEFAULT_PUSH_RELEASE)


class MiscProfile(dict):
    @staticmethod
    def get_args(**kwargs):
        return {get_opts_key(OptionsKey.DRYRUN): kwargs.get(
            get_opts_key(OptionsKey.DRYRUN),
            DEFAULT_GIT_REPO),
                get_opts_key(OptionsKey.EXPORT_OPTIONS): kwargs.get(
                    get_opts_key(OptionsKey.EXPORT_OPTIONS),
                    DEFAULT_EXPORT_OPTIONS)}

    @property
    def dry_run(self):
        return self.get(get_opts_key(OptionsKey.DRYRUN), DEFAULT_DRYRUN)

    @property
    def export_options(self):
        return self.get(get_opts_key(OptionsKey.EXPORT_OPTIONS),
                        DEFAULT_EXPORT_OPTIONS)


class LoggingProfile(dict):
    @staticmethod
    def get_args(**kwargs):
        return {get_opts_key(OptionsKey.VERBOSE): kwargs.get(
            get_opts_key(OptionsKey.VERBOSE),
            DEFAULT_GIT_PROFILE)}

    @property
    def verbose(self):
        return self.get(get_opts_key(OptionsKey.VERBOSE), DEFAULT_VERBOSE)


class Profile(iExporter):
    """
    Profile class to allow easy inspection of the profile sections.
    """
    _PROFILES = ['history', 'publish', 'build', 'vcs', 'misc', 'logging']

    def __init__(self):
        self.history = HistorianProfile()
        self.publish = PublisherProfile()
        self.build = BuilderProfile()
        self.vcs = VcsProfile()
        self.misc = MiscProfile()
        self.logging = LoggingProfile()

    def __str__(self):
        return 'Profile(%s): %s' % self.dry_run

    @property
    def _export_data(self):
        result = {}
        for name in Profile._PROFILES:
            d = {}
            d.update(getattr(self, name))
            result[name] = d
        return result

    def _update_data(self, d):
        """
        Update (freshen) from exported_data
        """
        for name in Profile._PROFILES:
            d[name] = getattr(self, name).update(d.get(name, dict()))
        return self

    @staticmethod
    def build(d):
        """
        Build (overwrite) a new class from exported_data.
        """
        return Profile()._update_data(d)

    @staticmethod
    def create(d):
        """
        Create a new class from a single-depth dict (ie: options).
        """
        result = dict()
        pp = zip(Profile._PROFILES,
                 [HistorianProfile, PublisherProfile, BuilderProfile,
                  VcsProfile, MiscProfile, LoggingProfile])
        for name, cls in pp:
            result[name] = getattr(cls, 'get_args')(**d)

        return Profile()._update_data(result)

    @property
    def dump(self):
        return pprint.pformat(self._export_data)


class NewProfile(object):
    @staticmethod
    def _validate_profile(d):
        return d

    @staticmethod
    def _load_profile(profile_path, silent=False):
        if not profile_path:
            return dict()
        if not os.path.exists(profile_path):
            if not silent:
                raise NoProfileFile(
                    'profile path does not exist: %s' % profile_path)
            return dict()
        try:
            return yaml.loads(open(profile_path))
        except Exception as err:
            raise ProfileLoadError(err,
                                   'Error parsing profile file (is it correct '
                                   'yaml format?): %s' % profile_path)

    @staticmethod
    def _update_profile(profile, kwargs):
        return update_dict(profile, kwargs)

    @staticmethod
    def _load_profile_from_env(env):
        return os.environ.get(env, None)

    @staticmethod
    def _get_profile_file(profile, env=DEFAULT_ENV):
        # Load from env first:
        profile_ = NewProfile._load_profile_from_env(env)

        # Use cmd-line profile otherwise:
        return profile_ if profile_ is not None else profile

    @staticmethod
    def build(**kwargs):
        """
        Factory method to do all the work of creating the profile dictionary
            from all provided sources.

        :param kwargs: kwargs to use / include in profile.
        :return: dict(profile)
        :ProfileLoadError - error in yaml loading (file exists but cannot be
            parsed).
        """
        profile = kwargs.get('profile', None)
        profile_env = kwargs.get('ENV')

        profile_file = kwargs.get('profile',
                                  NewProfile._get_profile_file(profile,
                                                               profile_env))
        loaded_profile = NewProfile._load_profile(profile_file, silent=True)
        validated_profile = NewProfile._validate_profile(loaded_profile)
        updated_profile = NewProfile._update_profile(validated_profile,
                                                     kwargs)

        return Profile.create(updated_profile)


if __name__ == '__main__':  # pragma no cover
    pass

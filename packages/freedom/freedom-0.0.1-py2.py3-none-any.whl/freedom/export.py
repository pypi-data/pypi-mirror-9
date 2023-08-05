# -*- coding: utf-8 -*-
"""
:summary: All data export, import is done through here.

:attention: Serialisation to json is attempted using the following libraries in
    order: (ujson, simplejson, json)
:author: Francis.horsman@gmail.com
"""

import copy
import sys
import pickle
from abc import abstractmethod, ABCMeta

import yaml
import msgpack
import six

from .defaults import DEFAULT_EXPORT_FORMAT, ExportFormat
from .errors import UnknownExportCodec, ExporterConfigurationError
from .logger import get_logger

try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        try:
            import json
        except ImportError:
            sys.exit('No json library available')


@six.add_metaclass(ABCMeta)
class iExporter(object):
    @abstractmethod
    def build(self, d):
        raise NotImplementedError

    @abstractmethod
    def create(self, d):
        raise NotImplementedError

    @abstractmethod
    def dump(self):
        raise NotImplementedError


_SUPPORTED_CODECS = {}


class CodecRegistry(type):
    def __new__(mcs, name, bases, dct):
        codec_format = dct.get('CODEC_FORMAT', None)
        if not bases == (object,) and not codec_format:
            raise ExporterConfigurationError(
                '%s is not configured correctly, it must specify a'
                'CODEC_FORMAT class attribute' % name)
        impl = dct.get('CODEC_IMPL')
        if impl is not None:
            dct['impl'] = impl
        cls = super(CodecRegistry, mcs).__new__(mcs, name, bases, dct)
        if name != 'ExporterCodec':
            _SUPPORTED_CODECS[codec_format] = cls
        return cls


@six.add_metaclass(CodecRegistry)
@six.add_metaclass(ABCMeta)
class ExporterCodec(object):
    @abstractmethod
    def loads(self, d, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def dumps(self, d, **kwargs):
        raise NotImplementedError


class JsonCodec(ExporterCodec):
    CODEC_IMPL = json
    CODEC_FORMAT = ExportFormat.JSON

    @staticmethod
    def loads(d, **kwargs):
        return JsonCodec.impl.loads(d, **kwargs)

    @staticmethod
    def dumps(d, **kwargs):
        return JsonCodec.impl.dumps(d, **kwargs)


class PickleCodec(ExporterCodec):
    CODEC_IMPL = pickle
    CODEC_FORMAT = ExportFormat.PICKLE

    @staticmethod
    def loads(d, **kwargs):
        return PickleCodec.impl.loads(d, **kwargs)

    @staticmethod
    def dumps(d, **kwargs):
        return PickleCodec.impl.dumps(d, **kwargs)


class YamlCodec(ExporterCodec):
    CODEC_IMPL = yaml
    CODEC_FORMAT = ExportFormat.YAML

    @staticmethod
    def loads(d, **kwargs):
        return YamlCodec.impl.load(d, **kwargs)

    @staticmethod
    def dumps(d, **kwargs):
        return YamlCodec.impl.dump(d, default_flow_style=False, **kwargs)


class MsgpackCodec(ExporterCodec):
    CODEC_IMPL = msgpack
    CODEC_FORMAT = ExportFormat.MSGPACK

    @classmethod
    def loads(cls, d, **kwargs):
        return cls.impl.unpackb(d, **kwargs)

    @classmethod
    def dumps(cls, d, **kwargs):
        return cls.impl.packb(d, **kwargs)


class CodecFactory(object):
    def __init__(self, profile):
        self.profile = profile
        self.supported_codecs = copy.deepcopy(_SUPPORTED_CODECS)

    def __call__(self, name):
        return self.get_codec(name)

    def get_codec(self, name):
        try:
            return self.supported_codecs[name]
        except KeyError:
            raise UnknownExportCodec(name)


class Exporter(object):
    def __init__(self, profile, logger=None):
        self.profile = profile
        self.logger = logger or get_logger('exporter')
        self.codec_factory = CodecFactory(profile)

        export_path = self.profile.misc.export_options
        if export_path is not None:
            self._export(export_path)

    def _export(self, path):
        self.dump(path, self.profile)

    def load(self, where, codec=None):
        return self.loads(open(where, 'r').read(), codec=codec)

    def loads(self, what, codec=None):
        codec = codec if codec is not None else ExportFormat.JSON

        # Now call the codec to render the data.
        return self.codec_factory.get_codec(codec).loads(what)

    def dump(self, where, what, codec=None):
        txt = self.dumps(what, codec=codec)
        open(where, 'w').write(txt)

    def dumps(self, what, codec=None):
        codec = codec if codec is not None else DEFAULT_EXPORT_FORMAT

        # Get the data if supported:
        if isinstance(what, iExporter):
            what = getattr(what, '_export_data')

        # Now call the codec to render the data.
        return self.codec_factory.get_codec(codec).dumps(what)

    def __str__(self):
        supported_codecs = ', '.join(
            sorted(self.codec_factory.supported_codecs.keys()))
        return 'Exporter codecs supported: %s' % supported_codecs


if __name__ == '__main__':  # pragma no cover
    pass

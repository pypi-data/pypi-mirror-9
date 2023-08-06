import hashlib
import os
import re

from requests.utils import default_user_agent as requests_user_agent

from okonomiyaki.file_formats.egg import LegacySpecDepend

import hatcher


_R_RUNTIME = re.compile("""
    ^(?P<language>[\w]+)_runtime
    _
    (?P<version>[^_]+)
    _
    (?P<build_system_version>[^_]+)
    _
    (?P<platform>[^_]+)
    _
    (?P<build>\d+)
    \.
    (?P<extension>.+$)
    """, re.VERBOSE)


class RuntimeMetadata(object):
    _PYTHON_VERSION_TO_PYTHON_TAG = {
        "3.4": "cp34",
        "3.3": "cp33",
        "3.2": "cp32",
        "3.1": "cp31",
        "3.0": "cp30",
        "2.7": "cp27",
        "2.6": "cp26",
        "2.5": "cp25",
    }
    _VERSION_PREFIX_RE = re.compile(r'^(?P<version>\d+\.\d+)\.\d+$')

    def __init__(self, language, version, build, platform,
                 build_system_version, file_format, path):
        self.language = language
        self.version = version
        self.build = build
        self.platform = platform
        self.build_system_version = build_system_version
        self.file_format = file_format
        self._sha256 = None
        self.path = path

    @property
    def full_version(self):
        return '{}-{}'.format(self.version, self.build)

    @property
    def python_tag(self):
        match = self._VERSION_PREFIX_RE.match(self.version)
        if match is None:
            raise ValueError(
                'Unrecognized Python version: {!r}'.format(self.version))
        version_prefix = match.group('version')
        if version_prefix not in self._PYTHON_VERSION_TO_PYTHON_TAG:
            raise ValueError(
                'Unsupported Python version: {!r}'.format(self.version))
        return self._PYTHON_VERSION_TO_PYTHON_TAG[version_prefix]

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def sha256(self):
        if self._sha256 is None:
            self._sha256 = compute_sha256(self.path)
        return self._sha256

    @classmethod
    def from_file(cls, path, platform=None):
        basename = os.path.basename(path)
        m = _R_RUNTIME.match(basename)
        if m is None:
            raise ValueError('Invalid format for {0}'.format(path))
        attrs = m.groupdict()
        attrs['file_format'] = attrs.pop('extension')
        attrs['build'] = int(attrs['build'])
        return cls(path=path, **attrs)


class EggMetadata(object):

    def __init__(self, legacy_spec_depend, path):
        self._legacy_spec_depend = legacy_spec_depend
        self._sha256 = None
        self.path = path

    @property
    def full_version(self):
        return '{}-{}'.format(
            self._legacy_spec_depend.version, self._legacy_spec_depend.build)

    @property
    def python_tag(self):
        return self._legacy_spec_depend.python_tag

    @property
    def name(self):
        return self._legacy_spec_depend.name

    @property
    def sha256(self):
        if self._sha256 is None:
            self._sha256 = compute_sha256(self.path)
        return self._sha256

    @classmethod
    def from_file(cls, path, platform):
        spec_depend = LegacySpecDepend.from_egg(path, platform)
        return cls(spec_depend, path)


def _hash_file(hasher, filename, block_size):
    with open(filename, "rb") as fp:
        while True:
            data = fp.read(block_size)
            if data == b"":
                break
            hasher.update(data)
    return hasher.hexdigest()


def compute_sha256(filename, block_size=16384):
    return _hash_file(hashlib.sha256(), filename, block_size)


def compute_md5(filename, block_size=16384):
    return _hash_file(hashlib.md5(), filename, block_size)


def hatcher_user_agent():
    return 'hatcher/{0} {1}'.format(
        hatcher.__version__, requests_user_agent())

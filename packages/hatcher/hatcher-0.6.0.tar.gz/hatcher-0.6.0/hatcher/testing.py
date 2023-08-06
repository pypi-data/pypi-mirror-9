from copy import deepcopy
import hashlib
import json
import os
import sys


if sys.version_info < (2, 7):
    import unittest2 as unittest  # noqa
else:
    import unittest  # noqa


def python_tag_from_metadata(metadata):
    if 'python_tag' in metadata:
        return metadata['python_tag']
    else:
        python = metadata['python']
        return 'cp{}'.format(''.join(python.split('.')))


NotGiven = object()


def legacy_index_entry_from_egg_metadata(
        metadata, available=True, python=NotGiven):
    metadata = deepcopy(metadata)
    metadata['full_version'] = '{version}-{build}'.format(
        version=metadata['version'], build=metadata['build'])
    if python is not NotGiven:
        metadata['python'] = python
    if 'python_tag' not in metadata:
        if metadata['python'] is None:
            tag = None
        else:
            tag = 'cp{}{}'.format(*metadata['python'].split('.'))
        metadata['python_tag'] = tag
    metadata['available'] = available
    metadata['mtime'] = round(metadata['mtime'])
    metadata['type'] = 'egg'
    metadata.pop('platform')
    metadata.pop('sha256')
    if 'product' not in metadata:
        metadata['product'] = None
    return metadata


def make_testing_egg_metadata(**kwargs):
    """Create metadata suitable for brood testing.

    Parameters
    ----------
    name : str
        The name of the package (e.g. "numpy").
    version : str
        The version of the package (e.g. "1.8.0").
    build : int
        The build number of the package (e.g. 2).
    md5 : str
        The md5sum of the package.
    sha256 : str
        The sha256 of the package.
    mtime : float
        The modification time of the file.
    packages : list of str
        The dependicies of the package.
    size : int
        The size of the resulting file.
    platform : str
        The platform for which the package has been built.
    python : str
        [Legacy] The version of python for which the package is built.
        This is mutually exclusive with the ``python_tag`` parameter.
    python_tag : str
        The Python runtime implmentation tag (PEP425).

    """
    valid_keys = {'name', 'version', 'build', 'md5', 'sha256', 'mtime',
                  'packages', 'size', 'platform', 'product', 'python',
                  'python_tag'}
    unexpected_args = {key: value for key, value in kwargs.items()
                       if key not in valid_keys}
    if unexpected_args != {}:
        raise RuntimeError(
            'Unexpected keyword arguments: {!r}'.format(unexpected_args))

    if 'python_tag' in kwargs and 'python' in kwargs:
        raise RuntimeError(
            'python_tag and python arguments are not compatible.')

    md5 = kwargs.pop('md5', None)
    sha256 = kwargs.pop('sha256', None)

    testing_st = os.stat(__file__)
    metadata = {
        "name": "dummy",
        "version": "1.0.1",
        "build": 1,
        "mtime": round(testing_st.st_mtime),
        "packages": [],
        "python": "2.7",
        "size": testing_st.st_size,
        "platform": "rh5-64",
    }
    if 'python_tag' in kwargs:
        metadata.pop('python')
    metadata.update(kwargs)

    metadata_json = json.dumps(metadata).encode('utf-8')
    if md5 is None:
        md5 = hashlib.md5(metadata_json).hexdigest()
    if sha256 is None:
        sha256 = hashlib.sha256(metadata_json).hexdigest()

    metadata['md5'] = md5
    metadata['sha256'] = sha256

    return metadata


class TestingEgg(object):
    """Dumb container to package up the path to a generated testing egg with
    its metadata, and actual md5 and sha256.

    """

    def __init__(self, path, filename, md5, sha256, metadata):
        self.path = path
        self.filename = filename
        self.md5 = md5
        self.sha256 = sha256
        self.metadata = metadata

    def __getattr__(self, name):
        if name in self.metadata:
            return self.metadata[name]
        raise AttributeError(name)

    @property
    def index_entry(self):
        return legacy_index_entry_from_egg_metadata(self.metadata)

    @property
    def packages(self):
        return self.metadata['packages'][:]

    @property
    def python(self):
        python = self.metadata.get('python', NotGiven)
        if python is NotGiven:
            raise AttributeError('python')
        return python

    @property
    def python_tag(self):
        python_tag = self.metadata.get('python_tag', NotGiven)
        if python_tag is not NotGiven:
            return python_tag
        try:
            return python_tag_from_metadata(self.metadata)
        except KeyError:
            raise AttributeError('python_tag')

    @property
    def key(self):
        return self.filename

    @property
    def full_version(self):
        return '{}-{}'.format(self.version, self.build)

    @property
    def egg_basename(self):
        return self.filename.split('-')[0]

    def __eq__(self, other):
        if not isinstance(other, TestingEgg):
            return NotImplemented
        return self.metadata == other.metadata

    def __ne__(self, other):
        return not (self == other)


def build_egg(metadata, content, dest_dir):
    from okonomiyaki.file_formats.egg import (
        Dependency, EggBuilder, LegacySpec, LegacySpecDepend)
    from okonomiyaki.platforms.legacy import LegacyEPDPlatform

    packages = [Dependency.from_spec_string(package)
                for package in metadata.get('packages', [])]
    python = metadata.get('python', NotGiven)
    python_tag = metadata.get('python_tag', NotGiven)
    platform = metadata['platform']
    legacy_spec_depend = LegacySpecDepend(
        name=metadata['name'],
        version=metadata['version'],
        build=metadata['build'],
        python=python if python is not NotGiven else None,
        python_tag=(python_tag if python_tag
                    is not NotGiven else None),
        packages=packages,
        _epd_legacy_platform=LegacyEPDPlatform.from_epd_platform_string(
            platform),
    )
    spec = LegacySpec(depend=legacy_spec_depend)
    with EggBuilder(spec, cwd=dest_dir) as builder:
        builder.add_usr_files_iterator(content.items())
    return builder.egg_path


def make_testing_egg(dest_dir, egg_basename=None, **kwargs):
    """Create a testing egg file.

    Paramaters
    ----------
    dest_dir : str
        The name of the directory where the egg will be created.

    In addition to the above, this accepts all parameters of
    :function:`.make_testing_egg_metadata`.

    Returns
    -------
    testing_egg : TestingEgg
        A container containing the path to the egg file and its
        metadata.

    """
    from hatcher.core.utils import compute_md5, compute_sha256
    metadata = make_testing_egg_metadata(**kwargs)
    egg_path = build_egg(metadata, {}, dest_dir)

    if egg_basename is not None:
        dirname = os.path.dirname(egg_path)
        basename = os.path.basename(egg_path)
        _, rest = basename.split('-', 1)
        new_basename = '{}-{}'.format(egg_basename, rest)
        new_path = os.path.join(dirname, new_basename)
        os.rename(egg_path, new_path)
        egg_path = new_path

    st = os.stat(egg_path)
    md5 = compute_md5(egg_path)
    sha256 = compute_sha256(egg_path)
    metadata['md5'] = md5
    metadata['sha256'] = sha256
    metadata['size'] = st.st_size
    metadata['mtime'] = round(st.st_mtime)
    filename = os.path.basename(egg_path)
    return TestingEgg(egg_path, filename, md5, sha256, metadata)

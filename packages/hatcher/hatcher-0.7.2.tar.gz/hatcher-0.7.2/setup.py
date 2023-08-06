# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import os
import subprocess

from setuptools import setup, find_packages

MAJOR = 0
MINOR = 7
MICRO = 2

IS_RELEASED = True

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env,
        ).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    try:
        out = _minimal_ext_cmd(['git', 'rev-list', '--count', 'HEAD'])
        git_count = out.strip().decode('ascii')
    except OSError:
        git_count = '0'

    return git_revision, git_count


def write_version_py(filename='hatcher/_version.py'):
    template = """\
# THIS FILE IS GENERATED FROM SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of hatcher._version
    # messes up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists('hatcher/_version.py'):
        # must be a source distribution, use existing version file
        try:
            from hatcher._version import git_revision as git_rev
            from hatcher._version import full_version as full_v
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "hatcher/_version.py and the build "
                              "directory before building.")
        import re
        match = re.match(r'.*?\.dev(?P<dev_num>\d+)\+.*', full_v)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = "Unknown"
        dev_num = '0'

    if not IS_RELEASED:
        fullversion += '.dev{0}+{1}'.format(dev_num, git_rev[:7])

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))


if __name__ == "__main__":
    write_version_py()
    from hatcher import __version__

    setup(name="hatcher",
          version=__version__,
          classifiers=[
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: BSD License',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
          ],
          author="Enthought Inc.",
          author_email="info@enthought.com",
          packages=find_packages(),
          install_requires=[
              "requests >= 2.4.0, < 2.6.0, != 2.5.1",
              "clint",
              "okonomiyaki",
              "six",
              "click >= 3.3, < 4.0",
              "pyyaml",
              "tabulate",
          ],
          entry_points="""
              [console_scripts]
              hatcher=hatcher.cli.main:main
          """,
          license="BSD")

# -*- coding: utf-8 -*-
# Copyright (c) 2015 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
import os
import subprocess

from setuptools import setup


MAJOR = 0
MINOR = 1
MICRO = 1

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

    def _fallback():
        try:
            out = _minimal_ext_cmd(['git', 'rev-list', '--count', 'HEAD'])
            git_count = out.strip().decode('ascii')
        except OSError:
            git_count = '0'
        return git_count

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    try:
        out = _minimal_ext_cmd(['git', 'describe', '--long'])
        out = out.strip().decode('ascii')
        if len(out) == 0:
            git_count = _fallback()
        else:
            last_tag, git_count, _ = out.split('-')
    except OSError:
        git_count = '0'

    return git_revision, git_count


def write_version_py(filename='graystruct/_version.py'):
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
    # write_version_py(), otherwise the import of graystruct._version
    # messes up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists('graystruct/_version.py'):
        # must be a source distribution, use existing version file
        try:
            from graystruct._version import git_revision as git_rev
            from graystruct._version import full_version as full_v
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "graystruct/_version.py and the build "
                              "directory before building.")
        import re
        match = re.match(r'.*?\.dev(?P<dev_num>\d+)\+.*', full_v)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = 'Unknown'
        dev_num = '0'

    if not IS_RELEASED:
        fullversion += '.dev{0}'.format(dev_num)

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))

    return fullversion


if __name__ == "__main__":
    install_requires = [
        'graypy',
        'structlog',
    ]

    __version__ = write_version_py()

    with open('README.rst') as fh:
        long_description = fh.read()

    setup(
        name='graystruct',
        version=__version__,
        url='https://github.com/sjagoe/graystruct',
        author='Simon Jagoe',
        author_email='simon@simonjagoe.com',
        classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: System :: Logging',
        ],
        description=('Integration between structlog and graylog GELF, '
                     'provided by graypy'),
        long_description=long_description,
        license='BSD',
        packages=['graystruct'],
        install_requires=install_requires,
        extras_require={'amqp': ['amqplib==1.0.2']},
    )

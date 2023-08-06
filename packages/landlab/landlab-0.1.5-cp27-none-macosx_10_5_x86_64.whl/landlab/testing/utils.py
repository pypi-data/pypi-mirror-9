#! /usr/bin/env python
import os
import subprocess
import types
import tempfile
import shutil

import yaml
from distutils.dir_util import mkpath


class cd(object):
    def __init__(self, dir):
        self._dir = dir

    def __enter__(self):
        self._starting_dir = os.path.abspath(os.getcwd())
        if not os.path.isdir(self._dir):
            mkpath(self._dir)
        os.chdir(self._dir)
        return os.path.abspath(os.getcwd())

    def __exit__(self, type, value, traceback):
        os.chdir(self._starting_dir)


class cdtemp(object):
    def __init__(self, **kwds):
        self._kwds = kwds
        self._tmp_dir = None

    def __enter__(self):
        self._starting_dir = os.path.abspath(os.getcwd())
        self._tmp_dir = tempfile.mkdtemp(**self._kwds)
        os.chdir(self._tmp_dir)
        return os.path.abspath(self._tmp_dir)

    def __exit__(self, type, value, traceback):
        os.chdir(self._starting_dir)
        shutil.rmtree(self._tmp_dir)


class mktemp(object):
    def __init__(self, **kwds):
        self._kwds = kwds
        self._tmp_dir = None

    def __enter__(self):
        self._tmp_dir = tempfile.mkdtemp(**self._kwds)
        return os.path.abspath(self._tmp_dir)

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self._tmp_dir)


def status(message):
    print ' '.join(['==>', message])


def check_output(*args, **kwds):
    kwds.setdefault('stdout', subprocess.PIPE)
    return subprocess.Popen(*args, **kwds).communicate()[0]


def system(*args, **kwds):
    verbose = kwds.pop('verbose', True)

    status(' '.join(args[0]))

    if verbose:
        call = subprocess.check_call
    else:
        call = check_output

    try:
        call(*args, **kwds)
    except subprocess.CalledProcessError:
        status('Error')
        raise


def which(prog, env=None):
    prog = os.environ.get(env or prog.upper(), prog)

    try:
        prog = check_output(['which', prog],
                            stderr=open('/dev/null', 'w')).strip()
    except subprocess.CalledProcessError:
        return None
    else:
        return prog


def pkg_config(name, opts):
    if isinstance(opts, types.StringTypes):
        opts = [opts]

    try:
        flags = check_output([which('pkg-config')] + opts + [name],
                             stderr=open('/dev/null', 'w')).strip()
    except subprocess.CalledProcessError:
        return None
    else:
        return flags

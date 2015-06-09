__author__ = 'arun'
from distutils import core
from distutils import errors
import logging
import os
import sys
import warnings

from setuptools import dist

from pbr import util


_saved_core_distribution = core.Distribution


def _monkeypatch_distribution():
    core.Distribution = dist._get_unpatched(core.Distribution)
    print "CORE [core.Distribution]: ", core.Distribution


def _restore_distribution_monkeypatch():
    core.Distribution = _saved_core_distribution


if sys.version_info[0] == 3:
    string_type = str
    integer_types = (int,)
else:
    string_type = basestring
    integer_types = (int, long)


def pbr(dist, attr, value):

    print "CORE [dist]: ", dist
    print "CORE [attr]: ", attr
    print "CORE [value]: ", value

    try:
        _monkeypatch_distribution()
        if not value:
            return

        print "CORE [isinstance(value, string_type)]: ", isinstance(value, string_type)
        if isinstance(value, string_type):
            path = os.path.abspath(value)
        else:
            path = os.path.abspath('setup.cfg')
        print "CORE [path]: ", path


        if not os.path.exists(path): raise errors.DistutilsFileError('The setup.cfg file %s does not exist.' % path)

        # Converts the setup.cfg file to setup() arguments
        try:
            attrs = util.cfg_to_args(path)
            print "CORE [attrs]: ", attrs
        except Exception:
            e = sys.exc_info()[1]
            logging.exception('Error parsing')
            raise errors.DistutilsSetupError('Error parsing %s: %s: %s' % (path, e.__class__.__name__, e))

        if attrs:
            for key, val in attrs.items():
                print "CORE [key]: ", key
                print "CORE [val]: ", val

                print "CORE [hasattr(dist.metadata, 'set_' + key)]: ",hasattr(dist.metadata, 'set_' + key)
                print "CORE [hasattr(dist.metadata, key)]: ",hasattr(dist.metadata, key)
                print "CORE [dist]: ",dist
                print "CORE [hasattr(dist, key)]: ",hasattr(dist, key)

                if hasattr(dist.metadata, 'set_' + key):
                    getattr(dist.metadata, 'set_' + key)(val)
                    print "CORE [getattr(dist.metadata, 'set_' + key)(val)]: ",getattr(dist.metadata, 'set_' + key)(val)
                elif hasattr(dist.metadata, key):
                    setattr(dist.metadata, key, val)
                    print "CORE [setattr(dist.metadata, key, val)]: ",setattr(dist.metadata, key, val)
                elif hasattr(dist, key):
                    setattr(dist, key, val)
                    print "CORE [setattr(dist, key, val)]: ",setattr(dist, key, val)
                else:
                    msg = 'Unknown distribution option: %s' % repr(key)
                    warnings.warn(msg)

        core.Distribution.finalize_options(dist)
        print "CORE [core.Distribution.finalize_options(dist)]: ",core.Distribution.finalize_options(dist)

        # if isinstance(dist.metadata.version, integer_types + (float,)):
        #     dist.metadata.version = str(dist.metadata.version)
        # 
        # ignore = ['pre_hook.*', 'post_hook.*']
        # dist.command_options = util.DefaultGetDict(lambda: util.IgnoreDict(ignore))
    finally:
        _restore_distribution_monkeypatch()
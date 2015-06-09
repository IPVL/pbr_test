__author__ = 'Hi'

import os
import re
import sys
import traceback

from collections import defaultdict

from distutils import log
from distutils.errors import (DistutilsOptionError, DistutilsModuleError,DistutilsFileError)
from setuptools.dist import Distribution

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import pbr.hooks

_VERSION_SPEC_RE = re.compile(r'\s*(.*?)\s*\((.*)\)\s*$')

D1_D2_SETUP_ARGS = {
    "name": ("metadata",),
    "version": ("metadata",),
    "author": ("metadata",),
    "install_requires": ("metadata", "requires_dist"),
    "packages": ("files",),
    "scripts": ("files",),
    "cmdclass": ("global", "commands"),
}

# setup() arguments that can have multiple values in setup.cfg
MULTI_FIELDS = ("install_requires",
                "packages",
                "scripts",
                "py_modules",
                "setup_requires",
                "cmdclass")


def resolve_name(name):
    parts = name.split('.')
    print "parts: ", parts
    cursor = len(parts) - 1
    print "cursor: ", cursor
    module_name = parts[:cursor]
    print "module_name: ", module_name
    attr_name = parts[-1]
    print "attr_name: ", attr_name

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name), fromlist=[attr_name])
            print "ret: ", ret
            break
        except ImportError:
            ret = ''

    for part in parts[cursor:]:
        try:
            print "part: ", part
            print "ret: ", ret
            ret = getattr(ret, part)
            print "last ret: ", ret
        except AttributeError:
            raise ImportError(name)

    return ret


def cfg_to_args(path='setup.cfg'):

    parser = configparser.SafeConfigParser()
    if not os.path.exists(path): raise DistutilsFileError("file '%s' does not exist" %os.path.abspath(path))

    parser.read(path)
    config = {} # An empty dictionary

    for section in parser.sections():
        config[section] = dict(parser.items(section))

    pbr.hooks.setup_hook(config)
    print "HOOKS PART ARE OVER. "

    kwargs = setup_cfg_to_setup_kwargs(config)
    entry_points = get_entry_points(config)

    if entry_points:
        kwargs['entry_points'] = entry_points

    # wrap_commands(kwargs)

    print "pbr.util.cfg_to_args: ", kwargs
    return kwargs


def setup_cfg_to_setup_kwargs(config):

    kwargs = {}

    for arg in D1_D2_SETUP_ARGS:
        if len(D1_D2_SETUP_ARGS[arg]) == 2:
            section, option = D1_D2_SETUP_ARGS[arg]

        elif len(D1_D2_SETUP_ARGS[arg]) == 1:
            section = D1_D2_SETUP_ARGS[arg][0]
            option = arg

        in_cfg_value = has_get_option(config, section, option)
        if not in_cfg_value:
            continue

        if arg in MULTI_FIELDS:
            in_cfg_value = split_multiline(in_cfg_value)

        if in_cfg_value:
            if arg == 'cmdclass':
                cmdclass = {}
                dist = Distribution()
                for cls_name in in_cfg_value:
                    cls = resolve_name(cls_name)
                    print "cls: ", cls
                    cmd = cls(dist)
                    print "cmd: ", cmd
                    cmdclass[cmd.get_command_name()] = cls
                    print "arg: ", arg
                    print "cmdclass[cmd.get_command_name()]", cmdclass[cmd.get_command_name()]
                    print "cmdclass: ", cmdclass 
                in_cfg_value = cmdclass

        kwargs[arg] = in_cfg_value

    return kwargs

def get_entry_points(config):
    if not 'entry_points' in config: return {}
    return dict((option, split_multiline(value)) for option, value in config['entry_points'].items())


def has_get_option(config, section, option):
    if section in config and option in config[section]:
        return config[section][option]
    elif section in config and option.replace('_', '-') in config[section]:
        return config[section][option.replace('_', '-')]
    else:
        return False


def split_multiline(value):
    print "[pbr.util.split_multiline -> First] value: ", value
    value = [element for element in (line.strip() for line in value.split('\n')) if element]
    print "[pbr.util.split_multiline -> Second] value: ", value
    return value


def split_csv(value):
    value = [element for element in (chunk.strip() for chunk in value.split(',')) if element]
    print "split_csv value: ", value
    return value


class DefaultGetDict(defaultdict):

    def get(self, key, default=None):
        if default is None:
            default = self.default_factory()
        return super(DefaultGetDict, self).setdefault(key, default)


class IgnoreDict(dict):

    def __init__(self, ignore):
        self.__ignore = re.compile(r'(%s)' % ('|'.join(
                                   [pat.replace('*', '.*')
                                    for pat in ignore])))

    def __setitem__(self, key, val):
        if self.__ignore.match(key):
            return
        super(IgnoreDict, self).__setitem__(key, val)

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

    print "[resolve_name] name: ", name
    parts = name.split('.')
    cursor = len(parts) - 1
    module_name = parts[:cursor]
    attr_name = parts[-1]

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name), fromlist=[attr_name])
            break
        except ImportError:
            if cursor == 0:
                raise
            cursor -= 1
            module_name = parts[:cursor]
            attr_name = parts[cursor]
            ret = ''

    for part in parts[cursor:]:
        try:
            ret = getattr(ret, part)
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
                    cmd = cls(dist)
                    cmdclass[cmd.get_command_name()] = cls
                in_cfg_value = cmdclass

        kwargs[arg] = in_cfg_value

    return kwargs

def get_entry_points(config):
    if not 'entry_points' in config: return {}
    return dict((option, split_multiline(value)) for option, value in config['entry_points'].items())


# def wrap_commands(kwargs):
#     dist = Distribution() # This is from setuptools.dist
#     dist.parse_config_files()
#
#     for cmd, _ in dist.get_command_list():
#         hooks = {}
#         if not hooks:
#             continue
#
#         if 'cmdclass' in kwargs and cmd in kwargs['cmdclass']:
#             cmdclass = kwargs['cmdclass'][cmd]
#         else:
#             cmdclass = dist.get_command_class(cmd)
#
#         new_cmdclass = wrap_command(cmd, cmdclass, hooks)
#         kwargs.setdefault('cmdclass', {})[cmd] = new_cmdclass


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

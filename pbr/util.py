__author__ = 'Hi'

import os
import re
import sys
import traceback
import ConfigParser as configparser

from collections import defaultdict

from distutils import log
from distutils.errors import (DistutilsOptionError, DistutilsModuleError,DistutilsFileError)
from setuptools.dist import Distribution

import pbr.hooks

D1_D2_SETUP_ARGS = {
    "name": ("katamata",),
    "version": ("katamata",),
    "author": ("katamata",),
    "install_requires": ("katamata", "requires_dist"),
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
    cursor = len(parts) - 1
    module_name = parts[:cursor]
    attr_name = parts[-1]

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name), fromlist=[attr_name])
            break
        except ImportError:
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
    kwargs = setup_cfg_to_setup_kwargs(config)
    entry_points = get_entry_points(config)

    if entry_points:
        kwargs['entry_points'] = entry_points

    print "kwargs: ", kwargs
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
    return dict((option, split_multiline(value)) for option, value in config['entry_points'].items())


def has_get_option(config, section, option):
    if section in config and option in config[section]:
        return config[section][option]
    elif section in config and option.replace('_', '-') in config[section]:
        return config[section][option.replace('_', '-')]
    else:
        return False


def split_multiline(value):
    value = [element for element in (line.strip() for line in value.split('\n')) if element]
    return value


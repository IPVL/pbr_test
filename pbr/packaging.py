from __future__ import unicode_literals

from distutils.command import install as du_install
from distutils import log
import os
import sys

import pkg_resources
from setuptools.command import easy_install
from setuptools.command import egg_info
from setuptools.command import install
from setuptools.command import install_scripts
from setuptools.command import sdist

class LocalInstall(install.install):
    command_name = 'install'
    def run(self):
        return du_install.install.run(self)

class LocalInstallScripts(install_scripts.install_scripts):
    command_name = 'install_scripts'
    print "The program has entered into LocalInstallScripts: "
    def run(self):
        import distutils.command.install_scripts

        self.run_command("egg_info")
        if self.distribution.scripts:
            distutils.command.install_scripts.install_scripts.run(self)
        else:
            self.outfiles = []
        if self.no_ep:
            return

        ei_cmd = self.get_finalized_command("egg_info")
        dist = pkg_resources.Distribution(ei_cmd.egg_base,pkg_resources.PathMetadata(ei_cmd.egg_base, ei_cmd.egg_info),ei_cmd.egg_name, ei_cmd.egg_version,)
        print "dist: ", dist
        bs_cmd = self.get_finalized_command('build_scripts')
        executable = getattr(bs_cmd, 'executable', easy_install.sys_executable)
        is_wininst = getattr(self.get_finalized_command("bdist_wininst"), '_is_running', False)

        if os.name != 'nt':
            get_script_args = override_get_script_args
        else:
            get_script_args = easy_install.get_script_args
            executable = '"%s"' % executable

        for args in get_script_args(dist, executable, is_wininst):
            self.write_script(*args)

class LocalManifestMaker(egg_info.manifest_maker):
    def add_defaults(self):
        sdist.sdist.add_defaults(self)
        self.filelist.append(self.template)
        self.filelist.append(self.manifest)
        ei_cmd = self.get_finalized_command('egg_info')
        self.filelist.include_pattern("*", prefix=ei_cmd.egg_info)


class LocalEggInfo(egg_info.egg_info):
    command_name = 'egg_info'
    print "The program has entered into LocalEggInfo: "
    def find_sources(self):
        manifest_filename = os.path.join(self.egg_info, "SOURCES.txt")
        print "manifest_filename: ", manifest_filename
        if (not os.path.exists(manifest_filename) or 'sdist' in sys.argv):
            mm = LocalManifestMaker(self.distribution)
            print "mm : ", mm
            mm.manifest = manifest_filename
            mm.run()
            self.filelist = mm.filelist
        else:
            self.filelist = egg_info.FileList()
            print "self.filelist: ", self.filelist
            for entry in open(manifest_filename, 'r').read().split('\n'):
                self.filelist.append(entry)


class LocalSDist(sdist.sdist):
    command_name = 'sdist'
    def run(self):
        print "This is the LocalSDist Run Method`"
        sdist.sdist.run(self)


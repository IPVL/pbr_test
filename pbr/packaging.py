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
    print "THE PROGRAM HAS ENTERED INTO LOCALINSTALL CLASS. "
    def run(self):
        return du_install.install.run(self)

class LocalInstallScripts(install_scripts.install_scripts):
    command_name = 'install_scripts'
    print "THE PROGRAM HAS ENTERED INTO LOCALINSTALLSCRIPT CLASS"
    def run(self):
        import distutils.command.install_scripts

        self.run_command("egg_info")
        print "LOCALINSTALLSCRIPTS [self.run_command]: ", self.run_command

        print "LOCALINSTALLSCRIPTS [self.distribution.scripts]: ", self.distribution.scripts
        if self.distribution.scripts:
            distutils.command.install_scripts.install_scripts.run(self)
            print "LOCALINSTALLSCRIPTS [distutils.command.install_scripts.install_scripts.run(self)]: ", distutils.command.install_scripts.install_scripts.run(self)
        else:
            self.outfiles = []
            print "LOCALINSTALLSCRIPTS [self.outfiles]: ", self.outfiles

        print "LOCALINSTALLSCRIPTS [self.no_ep]: ", self.no_ep
        if self.no_ep:
            return

class LocalManifestMaker(egg_info.manifest_maker):
    print "THE PROGRAM HAS ENTERED INTO LOCALMANIFESTMAKER CLASS."
    def add_defaults(self):
        sdist.sdist.add_defaults(self)
        self.filelist.append(self.template)
        self.filelist.append(self.manifest)
        ei_cmd = self.get_finalized_command('egg_info')
        print "LOCALMANIFESTMAKER [ei_cmd]: ", ei_cmd
        self.filelist.include_pattern("*", prefix=ei_cmd.egg_info)


class LocalEggInfo(egg_info.egg_info): # It is needed in the sdist command, not in install.
    command_name = 'egg_info'
    print "PROGRAM HAS ENTERED INTO LOCALEGGINFO CLASS. : "
    def find_sources(self):
        manifest_filename = os.path.join(self.egg_info, "SOURCES.txt")
        print "LOCALEGGINFO[manifest_filename]: ", manifest_filename
        if (not os.path.exists(manifest_filename) or 'sdist' in sys.argv):
            mm = LocalManifestMaker(self.distribution)
            print "LOCALEGGINFO[mm] : ", mm
            mm.manifest = manifest_filename
            print "LOCALEGGINFO[mm.manifest]: ", mm.manifest
            mm.run()
            self.filelist = mm.filelist
            print "LOCALEGGINFO [self.filelist]: ", self.filelist
        else:
            self.filelist = egg_info.FileList()
            print "LOCALEGGINFO [self.filelist]: ", self.filelist
            for entry in open(manifest_filename, 'r').read().split('\n'):
                self.filelist.append(entry)


class LocalSDist(sdist.sdist):
    command_name = 'sdist'
    print "PROGRAM HAS ENTERED INTO LOCALSDIST class."
    def run(self):
        print "This is the LocalSDist Run Method`"
        sdist.sdist.run(self)


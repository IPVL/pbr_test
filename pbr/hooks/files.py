__author__ = 'Hi'
import os
import sys

from pbr.hooks import base
from pbr import find_package


class FilesConfig(base.BaseConfig):

    section = 'files'

    def __init__(self, config, name):
        super(FilesConfig, self).__init__(config)
        self.name = name
        self.data_files = self.config.get('data_files', '')

    def save(self):
        self.config['data_files'] = self.data_files
        super(FilesConfig, self).save()


    def hook(self):
        packages = self.config.get('packages', self.name).strip()
        expanded = []
        for pkg in packages.split("\n"):
            if os.path.isdir(pkg.strip()):
                expanded.append(find_package.smart_find_packages(pkg.strip()))
        self.config['packages'] = "\n".join(expanded)


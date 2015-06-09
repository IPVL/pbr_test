__author__ = 'Hi'

from pbr.hooks import base


class MetadataConfig(base.BaseConfig):

    section = 'metadata'

    def hook(self):
        self.config['version'] = "1.0"

    def get_name(self):
        return self.config['name']

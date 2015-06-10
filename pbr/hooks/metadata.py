__author__ = 'Hi'

from pbr.hooks import base


class MetadataConfig(base.BaseConfig):

    section = 'katamata'

    def get_name(self):
        return self.config['name']

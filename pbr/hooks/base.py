__author__ = 'Hi'
class BaseConfig(object):

    section = None

    def __init__(self, config):
        self._global_config = config
        self.config = self._global_config.get(self.section, dict())
        self.pbr_config = config.get('pbr', dict())

    def run(self):
        self.hook()
        self.save()
        print "\n"

    def hook(self):
        pass

    def save(self):
        self._global_config[self.section] = self.config
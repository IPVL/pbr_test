__author__ = 'Hi'

from pbr.hooks import base


class CommandsConfig(base.BaseConfig):

    section = 'global'

    def __init__(self, config):
        super(CommandsConfig, self).__init__(config)
        self.commands = self.config.get('commands', "")
        print "\n"

    def save(self):
        self.config['commands'] = self.commands
        super(CommandsConfig, self).save()

    def add_command(self, command):
        self.commands = "%s\n%s" % (self.commands, command)

    def hook(self):
        self.add_command('pbr.packaging.LocalEggInfo')
        self.add_command('pbr.packaging.LocalSDist')
        self.add_command('pbr.packaging.LocalInstallScripts')
        self.add_command('pbr.packaging.LocalDevelop')


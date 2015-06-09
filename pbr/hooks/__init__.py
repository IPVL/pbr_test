from pbr.hooks import commands
from pbr.hooks import files
from pbr.hooks import metadata



def setup_hook(config):
    metadata.MetadataConfig(config).run()
    commands.CommandsConfig(config).run()
    files.FilesConfig(config, metadata.MetadataConfig(config).get_name()).run()


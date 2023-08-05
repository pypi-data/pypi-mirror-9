# -*- coding: utf-8 -*-
import os


exists = os.path.exists
pjoin = os.path.join
expanduser = os.path.expanduser


class Configuration(object):
    def __init__(self, data):
        self.__dict__.update(**data)


class ConfigurationReader(object):
    DEFAULT_TRIGGER = '.penv'
    DEFAULT_SKIP_FILE = '.skip'

    def read_defaults(self, config):
        config.update({
            'TRIGGER': os.environ.get('PENV_TRIGGER', self.DEFAULT_TRIGGER),
            'PLUGIN_PLACES': [
                pjoin(expanduser("~"), '.penv', '.plugins'),
            ],
            'SKIP_FILE': os.environ.get('PENV_SKIP_FILE', self.DEFAULT_SKIP_FILE),
        })
        return config

    def read_local_penv(self, config, root_new):
        plugins = config.get('PLUGIN_PLACES')

        # Some default, current-dir-location-related, places where I'd
        # like to find plugins. The idea is that ".penv" is NOT
        # under version control but ".penv-plugins" might be.
        plugins.append(root_new('.penv', '.plugins'))
        plugins.append(root_new('.penv-plugins'))

        skip_file_path = root_new(config.get('TRIGGER'),
                                  config.get('SKIP_FILE'))
        skip_file_exists = exists(skip_file_path)
        config.update({
            'PLUGIN_PLACES': plugins,
            'SKIP_FILE_PATH': skip_file_path,
            'SKIP_FILE_EXISTS': skip_file_exists,
        })
        return config

    def read(self, config, root_new):
        config = self.read_defaults(config)
        config = self.read_local_penv(config, root_new)
        return Configuration(config)


class ConfigurationMixin(object):
    configuration_reader = ConfigurationReader()

    def get_config(self, root_new):
        return self.configuration_reader.read({}, root_new)

# -*- coding: utf-8 -*-
"""
Definition of plugin registry etc...
"""
import os
import sys
import fnmatch
import importlib

import click

from . import bash


exists = os.path.exists


class Plugin(bash.BashMixin):
    def __init__(self, registry, config):
        self.registry = registry
        self.config = config

    def debug(self, msg, *args):
        msg = str(msg)
        sys.stdout.write('%s\n' % self.bash.echo(msg % args))

    # Invoked on: "penv init"
    #
    # Basically: what todo *after* ".penv" gets activated in *this*
    # directory I'm currently in. Therefore ".penv" is guaranteed to
    # exist when this method is invoked.
    def init(self, root_new):
        return []

    def on_activate(self, root_new, root_old):
        return []

    def on_deactivate(self, root_new, root_old):
        return []


# Very simple register
class PluginRegistry(list):
    def add(self, *plugin_class):
        self.extend(plugin_class)


registry = PluginRegistry()
# end / register


# buildin plugins
class AvailablePlugins(Plugin):
    """
    Shows information about all loaded plugins.
    """

    def format_plugin_info(self, plugin_class):
        module_path = '{p.__module__}.{p.__name__}'.format(p=plugin_class)
        module = importlib.import_module(plugin_class.__module__)
        info = plugin_class.__doc__ or '-- no docs --'
        return (""
            "{module_path}\n"
            "    Found in {module_file_path}\n"
            "    {info}\n"
        ).format(
            module_path=click.style(module_path, fg='green', bold=True),
            module_file_path=module.__file__,
            info=info,
        )

    def function_body(self):
        return self.bash.echo("\n".join(
            self.format_plugin_info(pcls) for pcls in self.registry
        ))

    def on_activate(self, root_new, root_old):
        return [
            self.bash.function("penv-plugins", self.function_body()),
        ]

    def on_deactivate(self, root_new, root_old):
        return [
            self.bash.unset_f("penv-plugins"),
        ]
# end / buildin plugins


# LOADING PLUGINS
def load(plugin_places, config):

    def filter_python_files(file_name):
        return fnmatch.fnmatch(file_name, "*.py")

    def load_builtins():
        registry.add(AvailablePlugins)

    def load_plugins_from(path):
        plugin_files = os.listdir(path)
        plugin_files = filter(filter_python_files, plugin_files)

        for plugin_file in plugin_files:
            module_name = plugin_file.rstrip(".py")
            importlib.import_module(module_name)

    def load():
        for place in plugin_places:
            if exists(place):
                sys.path.insert(0, place)
                load_plugins_from(place)
                sys.path.pop(0)

    if not registry:
        load_builtins()
        load()

    registry_copy = tuple(registry)
    return [pclass(registry_copy, config) for pclass in registry]
# end / LOADING PLUGINS

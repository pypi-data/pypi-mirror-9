# -*- coding: utf-8 -*-
import os

from . import bash
from . import conf
from . import plugins
from . import shell


abspath = os.path.abspath
pjoin = os.path.join
exists = os.path.exists


class PathCalculator(object):  # stupid name....
    def __init__(self, place):
        self.place = place

    def __call__(self, *path):
        absolute_here = abspath(self.place)  # always in the place where it was called
        return abspath(pjoin(absolute_here, *path))


class Penv(bash.BashMixin, conf.ConfigurationMixin):
    def get_plugins(self, root_new):
        config = self.get_config(root_new)
        return plugins.load(config.PLUGIN_PLACES, config)

    # init
    #
    # has nothing todo with the rest, but I don't know yet where to
    # put it. Supposed to be invoked on "$> penv init" command.
    def init_script(self, root_new):
        result = []
        for plugin in self.get_plugins(root_new):
            scripts = plugin.init(root_new)
            result.extend(scripts or [])
        return "\n".join(result)

    def init(self, place):
        # by default create only ".penv" directory and append:
        # "eval "$(penv scan)""
        root_new = PathCalculator(place)
        config = self.get_config(root_new)
        shell.mkdir_p(root_new(config.TRIGGER))
        return self.init_script(root_new)
    # end / init

    def deactivate_bash_script(self, root_new, root_old):
        result = []
        for plugin in self.get_plugins(root_new):
            scripts = plugin.on_deactivate(root_new, root_old)
            result.extend(scripts or [])
        return "\n".join(result)

    def activate_bash_script(self, root_new, root_old):
        result = []
        for plugin in self.get_plugins(root_new):
            scripts = plugin.on_activate(root_new, root_old)
            result.extend(scripts or [])
        return "\n".join(result)

    def setup(self, place):
        old_pwd = os.environ.get("OLDPWD")
        root_new = PathCalculator(place)
        root_old = PathCalculator(old_pwd)
        config = self.get_config(root_new)
        script_stream = bash.BashStream()

        script_stream.writeln('# Scanning: %s | OLDPWD=%s' % (place, old_pwd))
        location = root_new(config.TRIGGER)
        venv_exists = exists(location)
        skip_searching = config.SKIP_FILE_EXISTS

        auto_venv_is_active = os.environ.get("PENV_IS_ACTIVE")
        if auto_venv_is_active:
            script_stream.writeln('#     '
                'previous env found (%s), so deactivating...' % location)
            script_stream.writeln(self.deactivate_bash_script(root_new, root_old))
            script_stream.writeln(self.bash.unset("PENV_IS_ACTIVE"))
            del os.environ["PENV_IS_ACTIVE"]
            script_stream.writeln('#     ...deactivation done.')

        if venv_exists and not skip_searching:
            script_stream.writeln('#     '
                'new env found (%s) and it shouldn\'t be '
                'skipped, so generating activation scripts' % location)

            # Information on where I'll look for plugins
            script_stream.writeln('#     %s' % ('#' * 30))
            script_stream.writeln('#     Following places will be checked for plugins existance:')
            for place in config.PLUGIN_PLACES:
                script_stream.writeln('#        %s' % place)
            script_stream.writeln('#     %s' % ('#' * 30))

            script_stream.writeln(self.activate_bash_script(root_new, root_old))
            script_stream.writeln(self.bash.export("PENV_IS_ACTIVE", "True"))
            script_stream.writeln('#     generation script done.')

        if skip_searching:
            script_stream.writeln('# Skipping searching because of: %s' % config.SKIP_FILE_PATH)

        return venv_exists, skip_searching, script_stream

    # TODO: change it to iterative version
    def lookup(self, place, parent_stream=None):
        parent_stream = parent_stream or bash.BashStream()

        venv_exists, skip_searching, stream = self.setup(place)
        parent_stream.writeln(stream.getvalue())

        if place == "/":
            return parent_stream.getvalue()

        if not venv_exists and not skip_searching:
            return self.lookup(abspath(pjoin(place, "..")), parent_stream)

        return parent_stream.getvalue()

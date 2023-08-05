# -*- coding: utf-8 -*-
"""
Small helpers that makes easy to generate bash.
"""
import pipes
from cStringIO import StringIO


class BashStream(object):
    def __init__(self):
        self.out = StringIO()

    def getvalue(self):
        return self.out.getvalue()

    def writeln(self, text):
        self.out.write(text)
        self.out.write("\n")


class Bash(object):
    def echo(self, message):
        return "; ".join([
            'echo %s' % pipes.quote(msg)
            for msg in message.split("\n")
        ])

    def export(self, name, value):
        return 'export %s=%s' % (name, value)

    def source(self, file_path):
        return 'source %s' % file_path

    def unset(self, name):
        return 'unset %s' % name

    def unset_f(self, name):
        return 'unset -f %s' % name

    def function(self, name, definition):
        return 'function %s () { %s; }' % (name, definition)


class BashMixin(object):
    bash = Bash()

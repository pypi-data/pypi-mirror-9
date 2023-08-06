#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from . import Command
from . import CommandError
from ..package import Package, find_package


class RemoveCommand(Command):
    """Remove an installed plugin"""
    def execute(self):
        plugin = self.args.plugin

        if "." not in plugin:
            raise CommandError("plugin must contain almost author.plugin")

        plugin_dir = self.config.get("plugin_dir", None)

        if not plugin_dir or len(plugin_dir) == 0:
            raise CommandError("Missing plugin_dir in configuration")

        for x in find_package(path=plugin_dir, pattern=plugin):
            self.log.info("Removed plugin %s" % (str(x),))
            x.remove()

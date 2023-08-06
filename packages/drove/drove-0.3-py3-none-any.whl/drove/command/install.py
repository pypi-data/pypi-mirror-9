#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os

from . import Command
from . import CommandError

from ..package import Package

"""This module implements the ``install`` command which can be invoked from
the commandline.

For more help, please run:

.. code-block:: sh

    $ drove install -h

"""


class InstallCommand(Command):
    """This class extends :class:`Command` and implement the ``install``
    command used by drove client to install plugins.
    """
    def execute(self):
        plugin_dir = self.config.get("plugin_dir", None)
        plugin = self.args.plugin
        upgrade = self.args.upgrade

        index_url = self.args.index_url or \
                     self.config.get("catalog.url",
                                     "https://plugins.drove.io").strip("/")
        install_global = self.args.install_global

        if not plugin_dir:
            raise CommandError("'plugin_dir' is not configured")

        if install_global:
            plugin_dir = os.path.expanduser(plugin_dir[-1])
        else:
            plugin_dir = os.path.expanduser(plugin_dir[0])

        # If plugin string is an URL
        if plugin.split("://")[0] in ["http", "https", "ftp"]:
            package = Package.from_url(plugin, plugin_dir, upgrade)
        # If plugin string is file in the filesystem
        elif os.path.exists(plugin) and os.path.isfile(plugin):
            # If file is a tarball
            if plugin.endswith(".tar.gz"):
                package = Package.from_tarball(plugin, plugin_dir, upgrade)
            else:
                raise CommandError("Provided package file is not a tarball")
        else:
            package = Package.from_repo(
                plugin,
                plugin_dir,
                index_url,
                upgrade)

        self.log.info("Installed package successfully [%s]:%s" %
                      (package.name, package.version[0:6]))

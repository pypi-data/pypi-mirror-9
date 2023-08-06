#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import glob

from . import Command
from . import CommandError

from ..package import find_package

"""This module implements the ``list`` command which can be invoked from
the commandline.

For more help, please run:

.. code-block:: sh

    $ drove list -h

"""


class ListCommand(Command):
    """This class extends :class:`Command` and implement the ``list``
    command used by drove client to list installed plugins.
    """
    def execute(self):
        plugin_dir = self.config.get("plugin_dir", None)
        if not plugin_dir:
            raise CommandError("Missing plugin_dir in configuration")

        for pkg in find_package(path=plugin_dir):
            self.log.info(str(pkg))


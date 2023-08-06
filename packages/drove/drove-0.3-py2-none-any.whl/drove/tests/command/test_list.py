#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import unittest

from drove.config import Config
from drove.util.log import getLogger
from drove.command import CommandError
from drove.command.list import ListCommand

import drove


class TestListCommand(unittest.TestCase):
    def test_list_command(self, config=None):
        if config is None:
            config = Config()
            config["plugin_dir"] = [
                os.path.join(os.path.dirname(drove.__file__), "plugins")
            ]
        cmd = ListCommand(config, None, getLogger())
        assert cmd.__class__.__name__ == "ListCommand"
        cmd.execute()

    def test_list_command_missing_config(self):
        with self.assertRaises(CommandError):
            self.test_list_command(Config())

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import unittest

from drove import config
from drove.config import Config, ConfigError


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_file = os.path.join(
            os.path.dirname(os.path.abspath(config.__file__)),
            "config",
            "drove.conf"
        )

    def test_config_hierarchy(self):
        """Testing Config: hierarchy"""
        c = Config()
        c["value"] = "lowlevel"
        c["plugin.one.value"] = "value"
        c["plugin.one.othervalue"] = "other"
        c["plugin.two"] = "second"

        assert c.get_childs("plugin") == {"one", "two"}
        assert c.get_childs("plugin.one") == {"value", "othervalue"}
        assert c.get("plugin.one.value") == "value"
        assert c.get("plugin.two.value") == "lowlevel"

    def test_config_include(self):
        """Testing Config: include"""
        c = Config(os.devnull)
        c["include"] = self.config_file
        c.reload()
        assert c.get("plugin_dir", False)

    def test_config_default(self):
        """Testing Config: get with default"""
        c = Config()
        assert c.get("none", "value") == "value"

    def test_config_notfound(self):
        """Testing Config: value not found"""
        c = Config()
        with self.assertRaises(ConfigError):
            c.get("notfound")

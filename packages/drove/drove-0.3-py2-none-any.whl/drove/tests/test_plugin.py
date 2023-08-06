#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import unittest

from drove.config import Config
from drove.channel import Channel

import drove.plugin
from drove.plugin import Plugin, PluginManager


class TestingPlugin(Plugin):
    plugin_name = "test"

    class _mock_tread(object):
        def stop(self, *args, **kwargs):
            pass

    def read(self):
        self.emit(None)

    def write(self, channel):
        assert channel.__class__.__name__ == "Channel"

    def start(self):
        self.read_thread = self._mock_tread()
        self.write_thread = self._mock_tread()


class TestingFailedPlugin(Plugin):
    plugin_name = "test"

    def read(self):
        raise Exception

    def write(self, channel):
        raise Exception

    def _mock_log(self, *args, **kwargs):
        raise AssertionError


class TestingStartPlugin(Plugin):
    plugin_name = "test"
    value = []

    def read(self):
        self.value.append("read")

    def write(self, channel):
        self.value.append("write")


class TestPlugin(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.channel = Channel()
        self.channel.subscribe("test")

        self.config["plugin_dir"] = [
            os.path.join(os.path.dirname(drove.plugin.__file__), "plugins")
        ]
        self.config["read_interval"] = 0
        self.config["write_interval"] = 0

        self.testing_plugin = TestingPlugin(self.config, self.channel)
        self.testing_plugin.setup(self.config)

    def test_plugin_load(self):
        """testing plugin: load()"""
        x = Plugin.load("internal.log", self.config, self.channel)
        assert x.__class__.__name__ == "LogPlugin"

    def test_plugin_rw(self):
        """Testing Plugin: read() and write()"""
        self.testing_plugin._read()
        self.testing_plugin._write()

    def test_plugin_stop(self):
        """Testing Plugin: stop()"""
        self.testing_plugin.stop()

    def test_plugin_failed(self):
        """Testing Plugin: failing"""
        x = TestingFailedPlugin(self.config, self.channel)
        x.setup(self.config)
        x.log.error = x._mock_log

        with self.assertRaises(AssertionError):
            x._read()

        with self.assertRaises(AssertionError):
            x._write()

    def test_plugin_start(self):
        """Testing Plugin: start() with handlers"""
        with self.assertRaises(AssertionError):
            x = TestingStartPlugin(self.config, self.channel)
            x.start()
            assert "read" in x.value
            assert "write" in x.value

    def test_plugin_manager_loop(self):
        """Testing PluginManager: waiting loop"""
        x = PluginManager(self.config, self.channel)
        x.loop(1000, 0)

    def test_plugin_manager(self):
        """Testing PluginManager: basic behaviour"""
        self.config["plugin.internal.log"] = True
        x = PluginManager(self.config, self.channel)
        assert x.plugins[0].__class__.__name__ == "LogPlugin"
        x.plugins = [TestingPlugin(self.config, self.channel)]
        x.start_all()
        assert len(x) == 1
        assert len([i for i in x]) == 1
        x.stop_all()

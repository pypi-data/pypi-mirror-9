#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import unittest


from six import b, BytesIO

from drove.util import temp
from drove.config import Config
from drove.util.log import getLogger
from drove.package import PackageError
from drove.command import CommandError
from drove.command.install import InstallCommand

import drove.package as package

_test_result_msg = """{"name": "none.none", "url": "http://none",
                       "description": "none"}
"""

class TestInstallCommand(unittest.TestCase):
    name = "test.install"
    version = "0"
    index_url = "http://localhost"

    class _mock_str(str):
        pass

    def test_install_command(self, install_global=False, plugin=__file__):
        self.plugin = TestInstallCommand._mock_str(plugin)
        self.plugin.endswith = lambda x: True
        self.install_global = install_global
        self.upgrade = True

        config = Config()
        config["plugin_dir"] = ["none"]

        import drove.package
        with temp.variables({
            "drove.package.Package.from_tarballfd":
                staticmethod(lambda *a, **kw: self)
        }):
            cmd = InstallCommand(config, self, getLogger())
            assert cmd.__class__.__name__ == "InstallCommand"
            cmd.execute()

    def test_install_command_global(self):
        self.test_install_command(True)

    def test_install_command_repo(self):
        with self.assertRaises(PackageError):
            self.test_install_command(False, "invalid://")

        self.plugin = TestInstallCommand._mock_str("none.none")
        self.plugin.endswith = lambda x: True
        self.install_global = False
        self.upgrade = True

        config = Config()
        config["plugin_dir"] = ["none"]
        import drove.package
        with temp.variables({
            "drove.package.Package.from_repo":
                staticmethod(lambda *a, **kw: self)
        }):
            cmd = InstallCommand(config, self, getLogger())
            assert cmd.__class__.__name__ == "InstallCommand"
            cmd.execute()

        _urlopen = package.urllib.request.urlopen
        package.urllib.request.urlopen = lambda *a, **kw: BytesIO(
            b(_test_result_msg)
        )
        package.Package.from_url = staticmethod(
            lambda *a, **kw: package.Package(
                "none", "none",
                "12345678", "", "")
        )
        self.test_install_command(False, "none")


    def test_install_noplugindir(self):
        config = Config()
        self.plugin = "none"
        self.install_global = False
        self.upgrade = False

        with self.assertRaises(CommandError):
            cmd = InstallCommand(config, self, getLogger())
            cmd.execute()

    def test_install_filenotarball(self):
        config = Config()
        config["plugin_dir"] = os.path.dirname(__file__)
        self.plugin = __file__
        self.install_global = False
        self.upgrade = False

        with self.assertRaises(CommandError):
            cmd = InstallCommand(config, self, getLogger())
            cmd.execute()

    def test_install_fromurl(self):
        self.plugin = "http://none"
        self.install_global = False
        self.upgrade = False

        config = Config()
        config["plugin_dir"] = ["none"]

        with temp.variables({
            "drove.package.Package.from_url":
                staticmethod(lambda *a, **kw: self)
        }):
            cmd = InstallCommand(config, self, getLogger())
            assert cmd.__class__.__name__ == "InstallCommand"
            cmd.execute()

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import unittest
from drove.util.daemon import Daemon


class TestDaemon(unittest.TestCase):
    def setUp(self):
        self._os = os.name

    def tearDown(self):
        os.name = self._os

    def test_daemon(self):
        """Testing Daemon: invalid platform"""
        os.name = 'foo'
        with self.assertRaises(NotImplementedError):
            Daemon.create(lambda: None)

    def test_daemon_posix(self):
        """Testing Daemon: posix"""
        os.name = 'posix'
        Daemon.create(lambda: None)

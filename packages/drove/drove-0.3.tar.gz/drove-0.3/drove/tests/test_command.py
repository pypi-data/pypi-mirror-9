#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import unittest

from drove.command import Command


class TestCommand(unittest.TestCase):
    def test_command(self):
        cmd = Command.from_name("list", None, None, None)
        assert cmd.__class__.__name__ == "ListCommand"

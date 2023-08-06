#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import sys
import unittest

from drove.util.importer import load


class TestImporter(unittest.TestCase):

    def test_importer_default(self):
        """Testing importer.load: from standard library"""
        cl = load("unittest.main", "TestProgram")
        assert cl.__name__ == 'TestProgram'

    def test_importer_path(self):
        """Testing importer.load: from path"""
        path = os.path.dirname(__file__)
        cl = load("test_importer", "TestImporter", path=[path])
        assert cl.__name__ == 'TestImporter'

    def test_importer_module(self):
        """Testing importer.load: module"""
        mod = load("sys")
        assert mod == sys

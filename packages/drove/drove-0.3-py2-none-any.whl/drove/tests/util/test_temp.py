#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import sys
import unittest
from drove.util import temp


class TestTemp(unittest.TestCase):

    def _mock_flush(*args, **kwargs):
        pass

    def test_temp_variable(self):
        """Testing util.temp.variables: basic behaviour"""
        with temp.variables({"sys.argv": ['test_value']}):
            assert sys.argv[0] == 'test_value'
        assert sys.argv[0] != 'test_value'

        with temp.variables({"sys.stdout": self._mock_flush}):
            assert sys.stdout == self._mock_flush

        with self.assertRaises(ValueError):
            with temp.variables({"fail": None}):
                pass

    def test_temp_directory(self):
        """Testing util.temp.directory: basic behaviour"""
        with temp.directory() as tmp_dir:
            assert os.path.isdir(tmp_dir)
        assert not os.path.isdir(tmp_dir)

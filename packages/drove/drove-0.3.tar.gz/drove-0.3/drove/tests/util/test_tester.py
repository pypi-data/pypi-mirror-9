#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import unittest
from drove.util import temp
from drove.util import tester


class TestTemp(unittest.TestCase):

    def test_tester(self):
        """Testing util.tester.run_tests: basic behaviour"""

        with temp.variables({"sys.stderr": open(os.devnull, 'a')}):
            #  We need to fake stderr because sometimes coverage.py
            #  puts an error in stderr when tests are collected by
            #  tester. This only happened when test into test.
            tester.run_tests(os.path.dirname(__file__))

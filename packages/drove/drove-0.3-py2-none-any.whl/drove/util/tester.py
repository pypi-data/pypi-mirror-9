#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import unittest


def run_tests(path):
    """Run tests find in path and return a list of
    :class:`TesterResult` objects"""
    ret = []

    for test_path in [os.path.join(path, "tests"), os.path.join(path, "test")]:
        if os.path.isdir(test_path):
            suite = unittest.TestSuite()
            suite.addTests(unittest.TestLoader().discover(test_path))
            result = unittest.TestResult()
            suite.run(result)
            ret.append(result)
    return ret

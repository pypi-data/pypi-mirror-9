#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import time
import unittest
from drove.util.timer import Timer


def _mock_sleep(value):
    if value != 1000:
        raise ValueError(value)


def _testing_fn(argument, d):
    d["value"] = argument


def _testing_fn_raise():
    raise ValueError


def _fail(x):
    raise ValueError()


def _stop(x):
    def wrapper():
        x.running = False
    return wrapper


class TestTimer(unittest.TestCase):
    def setUp(self):
        self._sleep = time.sleep

    def tearDown(self):
        time.sleep = self._sleep

    def test_timer_stop(self):
        """Testing Timer: stop"""
        x = Timer(0.2, lambda: None)
        x.run()
        x.stop()
        x.wait(2, 0)  # increase to count green thread

    def test_timer(self):
        """Testing Timer: basic behaviour"""
        d = {}
        x = Timer(0.1, _testing_fn, "test", d)
        x.run()
        time.sleep(0.5)
        assert d["value"] == "test"
        x.stop()

    def test_not_running(self):
        """Testing Timer: not running thread"""
        x = Timer(0.1, lambda: None)
        x.running = True
        x.stop()
        x._run()

    def test_timer_except(self):
        """Testing Timer: internal run"""
        with self.assertRaises(ValueError):
            x = Timer(0.1, _testing_fn_raise)
            x.running = True
            x._run()

    def test_timer_sleep(self):
        """Testing Timer: internal sleep"""
        with self.assertRaises(ValueError):
            x = Timer(0.1, lambda: None)
            x.fun = _stop(x)
            x.running = True
            x._run()
            x.stop()
            time.sleep = _fail
            Timer.wait(-1, seconds=0.1)

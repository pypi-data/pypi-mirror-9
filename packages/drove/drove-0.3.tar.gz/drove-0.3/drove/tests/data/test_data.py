#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import unittest
from drove.data import Data


class TestData(unittest.TestCase):
    def test_data_dump_value(self):
        """Testing Data: Value from_dump()"""
        value = Data.from_dump("V|0|test|example|42.0|g")
        assert value.__class__.__name__ == "Value"

    def test_data_dump_event(self):
        """Testing Data: Event from_dump()"""
        event = Data.from_dump("E|0|test|example|2|message")
        assert event.__class__.__name__ == "Event"

    def test_data_malformed_type(self):
        """Testing Data: malformed data type"""
        with self.assertRaises(ValueError):
            Data.from_dump("ZZ|0")

    def test_data_malformed_value(self):
        """Testing Data: malformed value"""
        with self.assertRaises(ValueError):
            Data.from_dump("V|0")

    def test_data_malformed_event(self):
        """Testing Data: malformed event"""
        with self.assertRaises(ValueError):
            Data.from_dump("E|0")

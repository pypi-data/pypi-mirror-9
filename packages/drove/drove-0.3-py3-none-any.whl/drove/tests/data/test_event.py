#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import time
import unittest
from drove.data.event import Event
from drove.data.event import Severity


class TestEvent(unittest.TestCase):

    def test_event(self):
        """Testing Event: dump()"""
        event = Event("example", Severity.CRITICAL, "message",
                      nodename="test", timestamp=0)
        assert event.is_event()
        assert event.dump() == "E|0|test|example|2|message"

        event = Event("example", Severity.CRITICAL, "message", nodename="test")
        assert event.dump() == ("E|%d|test|example|2|message" %
                                (int(time.time()),))

    def test_event_dump(self):
        """Testing Event: from_dump()"""
        event = Event.from_dump("E|0|test|example|2|message")
        assert event.dump() == "E|0|test|example|2|message" == repr(event)

    def test_event_malformed(self):
        """Testing Event: malformed event"""
        with self.assertRaises(ValueError):
            Event.from_dump("E|0")

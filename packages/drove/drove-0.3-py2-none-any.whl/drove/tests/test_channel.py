#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import unittest
from drove.channel import Channel


class TestChannel(unittest.TestCase):

    def test_channel_subscription(self):
        """Testing Channel: subscription"""
        channel = Channel()
        channel.subscribe("test")
        assert "test" in channel.queues

    def test_channel_broadcast(self):
        """Testing Channel: publish broadcast"""
        channel = Channel()
        channel.subscribe("test")
        channel.publish("hello")
        assert [x for x in channel.receive("test")][0] == "hello"

    def test_channel_publish(self):
        """Testing Channel: publish topic"""
        channel = Channel()
        channel.subscribe("test")
        channel.subscribe("test2")
        channel.publish("hello", topic="test")
        assert [x for x in channel.receive("test")][0] == "hello"
        assert channel.queues["test2"].qsize() == 0

    def test_channel_publish_none(self):
        """Testing Channel: publish non-existant"""
        channel = Channel()
        with self.assertRaises(KeyError):
            channel.publish("bye", topic="fail")

    def test_channel_receive_none(self):
        """Testing Channel: receive non-existant"""
        channel = Channel()
        channel.subscribe("test")
        channel.publish("bye")
        with self.assertRaises(KeyError):
            [x for x in channel.receive("bye")]

    def test_channel_receive_empty(self):
        """Testing Channel: receive in empty queue"""
        channel = Channel()
        channel.subscribe("test")
        assert [x for x in channel.receive("test")] == []

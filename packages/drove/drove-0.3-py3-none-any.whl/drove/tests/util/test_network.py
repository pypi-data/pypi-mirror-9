#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import socket
import unittest
from drove.util import network


class TestNetwork(unittest.TestCase):

    def test_parse_addr(self):
        """Testing util.network: parse_addr() basic behaviour"""
        assert network.parse_addr("127.0.0.1:12", resolve=False) == \
            ("127.0.0.1", 12, socket.AF_INET)

        assert network.parse_addr("127.0.0.1", defport=12) == \
            ("127.0.0.1", 12, socket.AF_INET)

        assert network.parse_addr("[::1]:12") == \
            ("::1", 12, socket.AF_INET6)

        assert network.parse_addr("[::1]", defport=12) == \
            ("::1", 12, socket.AF_INET6)

        assert network.parse_addr("localhost:12") in [
            ("::1", 12, socket.AF_INET6), ("127.0.0.1", 12, socket.AF_INET)]

    def test_parse_addr_empty(self):
        """Testing util.network: parse_addr() empty address"""
        with self.assertRaises(ValueError):
            network.parse_addr("")

    def test_parse_addr_fail(self):
        """Testing util.network: parse_addr() bad address"""
        with self.assertRaises(ValueError):
            network.parse_addr("300.0.0.1:12")

    def test_parse_addr_fail_resolve(self):
        """Testing util.network: parse_addr() cannot resolve"""
        _mocked_getaddrinfo = lambda *a, **kw: None
        with self.assertRaises(ValueError):
            network.socket.getaddrinfo = _mocked_getaddrinfo
            network.parse_addr("127.0.0.1:12")

    def test_getfqdn(self):
        """Testing util.network: getfqdn()"""
        x = network.getfqdn
        x.reload()
        x()
        assert isinstance(str(x), str)

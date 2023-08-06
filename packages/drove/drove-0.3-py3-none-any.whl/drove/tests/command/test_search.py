#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import unittest

from six import b, BytesIO

from drove.config import Config
from drove.command import search
from drove.command import CommandError
from drove.util.log import getLogger

_test_result_msg = """{
   "results": [{"name": "none.none",
                "url": "http://none",
                "description": "none"}]
}
"""

_test_result_malformed = "{}"
_test_result_empty = """{
    "results": []
}
"""


class TestSearchCommand(unittest.TestCase):
    index_url = "http://localhost"

    def test_search(self, result=_test_result_msg):
        self.plugin = "none.none"

        config = Config()
        config["plugin_dir"] = ["none"]

        _urlopen = search.urllib.request.urlopen
        search.urllib.request.urlopen = lambda *a, **kw: BytesIO(
            b(result)
        )
        try:
            search.SearchCommand(config, self, getLogger()).execute()
        finally:
            search.urllib.request.urlopen = _urlopen

    def test_search_error(self):
        with self.assertRaises(CommandError):
            self.test_search(_test_result_malformed)

    def test_search_error_empty(self):
        self.test_search(_test_result_empty)

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import unittest
from drove.util.lexer import Lexer


class ExampleItem(object):
    def __init__(self, arg):
        self.item = "example"


class TestLexer(unittest.TestCase):

    def test_lexer(self):
        """Testing util.lexer.Lexer: basic behaviour"""
        x = Lexer()
        items = [i for i in x.parse("item1 arg1, item2 arg2.")]
        for item in items:
            assert item.__class__.__name__ == "LexerItem"

        assert [y.item for y in items] == ["arg1", "arg2"]

    def test_lexer_without_term(self):
        """Testing util.lexer.Lexer: without terminator"""
        x = Lexer()
        items = [i for i in x.parse("item1 arg1, item2 arg2")]
        for item in items:
            assert item.__class__.__name__ == "LexerItem"

        assert [y.item for y in items] == ["arg1", "arg2"]

    def test_lexer_add_parser(self):
        """Testing util.lexer.Lexer: addItemParser()"""
        x = Lexer()
        x.addItemParser("item1", ExampleItem)

        items = [i for i in x.parse("item1 arg1, item2 arg2")]
        assert [y.__class__.__name__ for y in items] == \
            ["ExampleItem", "LexerItem"]

        assert [y.item for y in items] == ["example", "arg2"]

    def test_lexer_ignore_words(self):
        """Testing util.lexer.Lexer: addItemParser() with ignore_words"""
        x = Lexer()
        x.addItemParser("item1", ExampleItem, ignore_words=["ignore"])

        items = [i for i in x.parse("item1 ignore arg1.")]
        assert [y.__class__.__name__ for y in items] == ["ExampleItem"]

        items = [i for i in x.parse("item1 arg1 ignore.")]
        assert [y.__class__.__name__ for y in items] == ["ExampleItem"]

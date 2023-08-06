#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module provides a basic lexer utility.
"""

import shlex


class LexerItem(object):
    def __init__(self, *args):
        """This item is a basic unit in lexer, and it's used when
        no other class matching with an item."""
        self.item = " ".join(args)


class Lexer(object):
    def __init__(self, basic_class=LexerItem):
        """This is a simple lexer class, which can be used
        to position keyword parsing.

        Let's considerer some terminators, for example
        the character ";", then considerer two keywords
        "do" and "done", then the parsing of::

            do something; done

        Return a list of parsed objects.

        ObjectDo(something), ObjectDone()

        By default use :class:`LexerItem` as default
        class for parsed objects.


        More complex usage:

        >>> class ItemIf(object):
        ...   def __init__(self, key, comparisson, value):
        ...     self.key = key
        ...     self.comparisson = comparisson
        ...     self.value = value
        >>> x = Lexer()
        >>> x.addItemParser("if", ItemIf)
        >>> x.parse("if key > 100, then WARNING")
        [<ItemIf objet>, <LexerItem object: WARNING>]

        :type basic_class: class
        :param basic_class: the class to use when find a item
            without associated keyword class.
        """
        self.basic_class = basic_class
        self.item_parsers = {}
        self.ignore_words = {}

    def addItemParser(self, keyword, item_class=None, ignore_words=[]):
        """Add new item parser in lexer

        :type keyword: str
        :param keyword: keyword to find for this item parser
        :type item_class: class
        :param item_class: the class to instanciate for this
            keyword.
        """
        item_class = item_class or self.basic_class
        self.ignore_words[keyword] = ignore_words
        self.item_parsers[keyword] = item_class

    def parse(self,
              text,
              whitespace=" \t\r\n",
              wordchars=".,_-:;*><=!",
              commenters="#",
              quotes='\'"',
              terminators=".;,"):
        """Parse a text

        :type text: str
        :param text: the text to be parsed
        :type whitespace: str
        :param whitespace: a list (in string form) of
            items to be declared as whitespaces
        :type wordchars: str
        :param wordchars: a list (in string form) of
            chars which are part of word for the parser.
        :type commenters: str
        :param commenters: a list of chars used as comenter indicator.
        :type quotes: str
        :param quotes: a list of chars used as quotes for strings.
        :type terminators: str
        :param terminators: a list of chars used as terminators for sentences.
        """
        if text[-1] not in terminators:
            text += terminators[0]

        lex = shlex.shlex(text)
        lex.whitespace = whitespace
        lex.wordchars += wordchars
        lex.commenters = commenters
        lex.quotes = quotes

        words = []

        for token in lex:
            words.append(token.rstrip(terminators))
            if token[-1] in terminators and len(words) != 0:
                if words[0] in self.item_parsers:
                    args = [x for x in words[1:]
                            if x not in self.ignore_words[words[0]]]
                    yield self.item_parsers[words[0]](*args)
                else:
                    yield self.basic_class(*words[1:])
                words = []

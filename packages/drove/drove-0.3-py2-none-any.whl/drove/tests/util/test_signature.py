#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
import hashlib
import unittest
from drove.util.signature import hmac_fd


RESULT_HASH = '58e788c2210dd61f5d040b814a1416e5526' + \
              'cf0ddf59b3f3462ae19ea696746ee'


class TestSignature(unittest.TestCase):

    def test_hmac_fd(self):
        """Testing util.signature.hmac_fd: default hahser"""

        sample_file = os.path.join(os.path.dirname(__file__),
                                   "test_lexer.py")

        with open(sample_file, 'rb') as f:
            self.assertEquals(hmac_fd(f), RESULT_HASH)

        with open(sample_file, 'rb') as f:
            self.assertEquals(hmac_fd(f, hasher=hashlib.sha256()),
                RESULT_HASH)

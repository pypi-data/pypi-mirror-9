#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module provides signature functions for messages and files.
"""

import hashlib

class Signature(object):
    def __init__(self, hasher=None):
        self.hasher = hasher or hashlib.sha256()

    def update(self, bs):
        return self.hasher.update(bs)

    def hexdigest(self):
        return self.hasher.hexdigest()


def hmac_fd(fd, hasher=None, blocksize=65536):
    """Get HMAC for a file

    :param fd: a file object opened in read binary mode
    :param hasher: a hasher object provided by hashlib, use sha256
        by default
    :param blocksize: the blocksize to read in chunks the file
        to optimize memory, by default 65536 bytes.
    """
    hasher = Signature(hasher)

    buf = fd.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fd.read(blocksize)
    return hasher.hexdigest()

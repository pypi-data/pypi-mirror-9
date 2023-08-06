#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import unittest
from drove.util import log as drove_log


class TestLog(unittest.TestCase):

    def test_log_getdefaultlogger(self):
        """Testing log: getDefaultLogger()"""
        assert drove_log.getDefaultLogger() == \
            drove_log.logging.getLogger("drove.util.log.default")

    def test_log_socket(self):
        """Testing Logger: get_syslog_socket()"""
        import sys
        log = drove_log.Logger()

        sys.platform = "linux2"
        assert log.get_syslog_socket() == "/dev/log"

        sys.platform = "freebsd"
        assert log.get_syslog_socket() == "/var/run/log"

        sys.platform = "darwin"
        assert log.get_syslog_socket() == "/var/run/syslog"

        sys.platform = "unknown"
        assert log.get_syslog_socket() == "/dev/log"

        sys.platform = "win32"
        log = drove_log.Logger(syslog=True)
        del sys

    def test_log_getlogger(self):
        """Testing Logger: getLogger()"""
        log = drove_log.getLogger()
        assert drove_log.getLogger() == log

    def test_log_applogger_syslog(self):
        """Testing Logger: syslog"""
        log = drove_log.Logger(syslog=True)
        assert "SysLogHandler" in [x.__class__.__name__ for x in log.handlers]

    def test_log_applogger_logfile(self):
        """Testing Logger: logfile"""
        log = drove_log.Logger(logfile="/dev/null")
        assert "RotatingFileHandler" in \
            [x.__class__.__name__ for x in log.handlers]

    def test_log_applogger_console(self):
        """Testing Logger: console"""
        log = drove_log.Logger(console=True)
        assert "StreamHandler" in \
            [x.__class__.__name__ for x in log.handlers]

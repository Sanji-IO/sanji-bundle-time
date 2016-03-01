#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import logging
import unittest
from sanji.model_initiator import ModelInitiator
from mock import Mock
from mock import patch

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
    from systime.ntp import Ntp
    from systime.ntp import NtpDate
except ImportError as e:
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)


class TestFunctionClass(unittest.TestCase):

    def test_NtpDate(self):
        server = "test.ntp.org"
        with patch("systime.ntp.subprocess") as subprocess:
            subprocess.call.return_value = 0
            NtpDate(server)
            subprocess.call.assert_any_call("hwclock -w", shell=True)

            subprocess.call.reset_mock()
            subprocess.call.return_value = 1
            NtpDate(server)
            subprocess.call.assert_any_call(["ntpdate", server])


class TestNtpClass(unittest.TestCase):

    def setUp(self):
        path_root = os.path.dirname(os.path.realpath(__file__)) + "/../../"
        try:
            os.unlink(path_root + "data/ntp.json")
            os.unlink(path_root + "data/ntp.json.backup")
        except:
            pass
        self.model = ModelInitiator("ntp", path_root)
        self.ntp = Ntp(self.model)

    def tearDown(self):
        self.ntp.stop()
        self.ntp = None

    def test_start(self):
        self.ntp._ntp_thread = Mock()

        # case 1: previous daemon isn't stop
        self.ntp._ntp_thread.is_alive.return_value = True
        self.ntp._ntp_thread.start.return_value = None
        with self.assertRaises(RuntimeError):
            self.ntp.start()
            self.ntp._ntp_thread.start.assert_called_once_with()
        self.ntp.stop()
        # stop() will reinitialize Thread Object so we have to give new Mock
        self.ntp._ntp_thread = Mock()

        # case 2: normal
        self.ntp._ntp_thread.is_alive.return_value = False
        self.ntp.start()
        self.ntp._ntp_thread.start.assert_called_once_with()

    def test_update(self):
        self.ntp.stop = Mock()
        self.ntp.start = Mock()
        with patch("systime.ntp.NtpDate") as NtpDate:
            self.ntp.update({"enable": True})
            NtpDate.assert_called_once_with(self.model.db["ntp"]["server"])
            self.ntp.stop.assert_called_once_with()
            self.ntp.start.assert_called_once_with()

    def test__ntp_update(self):
        with patch("systime.ntp.NtpDate") as NtpDate:
            def stop(server):
                self.ntp._ntp_deamon_event.set()
            NtpDate.side_effect = stop
            self.model.db["ntp"]["interval"] = 0.001
            self.ntp._ntp_update()
            NtpDate.assert_called_once_with(self.model.db["ntp"]["server"])


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("Ntp")
    unittest.main()

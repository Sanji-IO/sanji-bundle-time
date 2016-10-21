#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import logging
import unittest

from mock import patch
from datetime import datetime

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
    from systime.systime import SysTime
except ImportError as e:
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)


class TestTimeClass(unittest.TestCase):

    def test_get_system_time(self):
        self.assertEqual(
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M")[0:13],
            SysTime.get_system_time()[0:13])

    def test_set_system_time(self):
        with patch("systime.systime.subprocess") as subprocess:
            # case 1: command success
            subprocess.call.return_value = 0
            t = "2015-03-26T16:27:48.611441Z"
            ans_t = "032616272015"
            self.assertTrue(SysTime.set_system_time(t))
            subprocess.call.assert_called_with(
                "date --utc %s; hwclock -w" % ans_t, shell=True)

            # case 2: command failed
            subprocess.call.return_value = 1
            self.assertFalse(SysTime.set_system_time(t))

            # case 3: invaild input
            with self.assertRaises(ValueError):
                SysTime.set_system_time("2015-0-26T16:27:48.611441Z")

    def test_set_system_timezone(self):
        with patch("systime.systime.subprocess") as subprocess:
            # case 1: command success
            subprocess.call.return_value = 1
            self.assertFalse(SysTime.set_system_timezone("Asia/Bangkok"))

            # case 2: command failed
            subprocess.call.return_value = 0
            self.assertTrue(SysTime.set_system_timezone("Asia/Dhaka"))

            # case 3: invaild timezone string
            with self.assertRaises(ValueError):
                SysTime.set_system_timezone("Asia/Puli")


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("SysTime")
    unittest.main()

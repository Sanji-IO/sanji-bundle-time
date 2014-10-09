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
        self.assertEqual(datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                         SysTime.get_system_time())

    def test_set_system_time(self):
        with patch("systime.systime.subprocess") as subprocess:
            # case 1: command success
            subprocess.call.return_value = 1
            t = "1988-10-21T00:00:00.000Z"
            self.assertFalse(SysTime.set_system_time(t))
            subprocess.call.assert_any_call("date %s; hwclock -w" % t,
                                            shell=True)

            # case 2: command failed
            subprocess.call.return_value = 0
            self.assertTrue(SysTime.set_system_time(t))
            subprocess.call.assert_any_call("date %s; hwclock -w" % t,
                                            shell=True)

            # case 3: invaild input
            with self.assertRaises(ValueError):
                SysTime.set_system_time("19881-1T00:00:00.000Z")

    def test_set_system_timezone(self):
        with patch("systime.systime.subprocess") as subprocess:
            # case 1: command success
            subprocess.call.return_value = 1
            self.assertFalse(SysTime.set_system_timezone("+07:00,0"))

            # case 2: command failed
            subprocess.call.return_value = 0
            self.assertTrue(SysTime.set_system_timezone("+06:00,0"))

            # case 3: invaild timezone string
            with self.assertRaises(ValueError):
                SysTime.set_system_timezone("+06:00,3")


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("SysTime")
    unittest.main()

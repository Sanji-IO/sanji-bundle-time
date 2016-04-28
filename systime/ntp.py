#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from time import sleep
from time import time
from threading import Event
from threading import Thread

import logging
import math
import sh
from sh import TimeoutException

_logger = logging.getLogger("sanji.time")


def NtpDate(server):
    try:
        sh.ntpdate(server, _timeout=30)
        _logger.info("NTP update successfully")
    except TimeoutException:
        _logger.info("NTP update timeout or system date has been changed")
    except Exception as e:
        _logger.info("NTP update failed")
        _logger.warning(e)
        return

    try:
        sh.hwclock("-w", _timeout=10)
    except Exception as e:
        _logger.info("Failed to sync to RTC")
        _logger.warning(e)


class Ntp(object):

    def __init__(self, model):
        self.model = model
        self._ntp_deamon_event = Event()
        self._ntp_thread = Thread(target=self._ntp_update)
        self._ntp_thread.daemon = True
        if self.model.db["ntp"]["enable"] is True:
            self.start()

    def update(self, config):
        # Update config
        self.model.db["ntp"] = dict(
            self.model.db["ntp"].items() + config.items())

        # restart ntp daemon, if enable otherwise stop it.
        self.stop()
        if self.model.db["ntp"]["enable"] is True:
            NtpDate(self.model.db["ntp"]["server"])
            self.start()

        self.model.save_db()
        return True

    def stop(self):
        _logger.debug("stop ntp daemon")
        if self._ntp_thread.is_alive():
            self._ntp_deamon_event.set()
            self._ntp_thread.join()
            # reinitialize Thread Object
            self._ntp_deamon_event.clear()
            self._ntp_thread = Thread(target=self._ntp_update)
            self._ntp_thread.daemon = True
            return True
        return False

    def start(self):
        _logger.debug("start ntp daemon")
        if self._ntp_thread.is_alive():
            raise RuntimeError("Stop previous ntp daemon first.")

        self._ntp_thread.start()

    def _ntp_update(self):
        prev_time = time()
        while not self._ntp_deamon_event.is_set():
            time_diff = math.fabs(prev_time - time())
            if time_diff < self.model.db["ntp"]["interval"]:
                sleep(1)
                continue

            try:
                NtpDate(self.model.db["ntp"]["server"])
            except Exception as e:
                _logger.warning(e)
            finally:
                prev_time = time()

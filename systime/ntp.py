#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from time import sleep
from time import time
from threading import Event
from threading import Thread

import logging
import math
import subprocess

logger = logging.getLogger("Time")


def NtpDate(servers):
    rc = subprocess.call(["ntpdate", servers])
    logger.debug("NTP update %s." % "successfully"
                 if rc == 0 else "failed")

    return rc


class Ntp(object):

    def __init__(self, config):
        self.config = config
        self._ntp_deamon_event = Event()
        self._ntp_thread = Thread(target=self._ntp_update)

    def update(self, config):
        # Update config
        self.config = dict(self.config.items() + config.items())

        # restart ntp daemon, if enable otherwise stop it.
        self.stop()
        if self.config["enable"] == 1:
            NtpDate(self.config["servers"])
            self.start()

    def stop(self):
        if self._ntp_thread.is_alive():
            self._ntp_deamon_event.set()
            self._ntp_thread.join()
            # reinitialize Thread Object
            self._ntp_thread = Thread(target=self._ntp_update)
            return True
        return False

    def start(self):
        if self._ntp_thread.is_alive():
            raise RuntimeError("Stop previous ntp daemon first.")

        self._ntp_thread.start()

    def _ntp_update(self):
        prev_time = time()
        while not self._ntp_deamon_event.is_set():
            time_diff = math.fabs(prev_time - time())
            if time_diff < self.config["interval"]:
                sleep(1)
                continue

            NtpDate(self.config["servers"])

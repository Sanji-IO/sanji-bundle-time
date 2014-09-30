#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from threading import Event


class Ntp(object):

    def __init__(self):
        self.config = {
            "enable": 0,
            "servers": [],
            "interval": 3600
        }
        self.ntp_deamon_event = Event()

    def update(self, config):
        pass

    def _ntp_thread(self):
        while not self.ntp_deamon_event.is_set():
            pass

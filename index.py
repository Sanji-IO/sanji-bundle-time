#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt
from systime.time import Time

logger = logging.getLogger()


class Index(Sanji):

    def init(self, *args, **kwargs):
        pass

    @Route(methods="get", resource="/system/time")
    def get_time(self, message, response):
        response(data={"time": Time.get_system_time()})

    @Route(methods="get", resource="/system/time/ntp")
    def get_ntp(self, message, response):
        response(data={"time": ""})


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("Time")
    index = Index(connection=Mqtt())
    index.start()

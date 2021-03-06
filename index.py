#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import logging
from sanji.core import Sanji
from sanji.core import Route
from sanji.model_initiator import ModelInitiator
from systime.ntp import Ntp
from systime.systime import SysTime

from voluptuous import Schema
from voluptuous import REMOVE_EXTRA
from voluptuous import Range
from voluptuous import All
from voluptuous import Length
from voluptuous import Optional
from datetime import datetime

_logger = logging.getLogger("sanji.time")


def Timestamp(value):
    datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    return value


class Index(Sanji):

    PUT_SCHEMA = Schema({
        Optional("time"): Timestamp,
        Optional("timezone"): All(str, Length(0, 255)),
        Optional("ntp"): {
            "enable": bool,
            "server": All(str, Length(1, 2048)),
            "interval": All(int, Range(min=60, max=60*60*24*30))
        }
    }, extra=REMOVE_EXTRA)

    def init(self, *args, **kwargs):
        path_root = os.path.abspath(os.path.dirname(__file__))
        self.model = ModelInitiator("ntp", path_root)
        self.ntp = Ntp(self.model)

    @Route(methods="get", resource="/system/time")
    def get(self, message, response):
        realtime_data = {
            "time": SysTime.get_system_time()
        }

        return response(
            data=dict(self.model.db.items() + realtime_data.items()))

    @Route(methods="get", resource="/system/zoneinfo")
    def get_zoneinfo(self, message, response):
        zoneinfo = SysTime.get_system_timezone_list()

        return response(data=dict(zoneinfo))

    @Route(methods="put", resource="/system/time", schema=PUT_SCHEMA)
    def put(self, message, response):
        rc = None
        try:
            # update ntp settings
            if "ntp" in message.data:
                rc = self.ntp.update(message.data["ntp"])
                if rc is False:
                    raise RuntimeWarning("Update ntp settings failed.")
                self.model.db["ntp"] = dict(self.model.db["ntp"].items() +
                                            message.data["ntp"].items())

            # change timezone
            if "timezone" in message.data:
                rc = SysTime.set_system_timezone(message.data["timezone"])
                if rc is False:
                    raise RuntimeWarning("Change timezone failed.")
                self.model.db["timezone"] = message.data["timezone"]

            # manual change sys time
            if "time" in message.data:
                if self.model.db["ntp"]["enable"] is True:
                    _logger.debug("NTP enabled. skipping time setup.")
                else:
                    rc = SysTime.set_system_time(message.data["time"])
                    if rc is False:
                        raise RuntimeWarning("Change system time failed.")

            if rc is None:
                return response(code=400,
                                data={"message": "No input paramters."})
            else:
                self.model.save_db()
        except Exception as e:
            _logger.debug(e, exc_info=True)
            code = 400 if not isinstance(e, RuntimeWarning) else 500
            return response(code=code, data={"message": str(e)})

        realtime_data = {
            "time": SysTime.get_system_time()
        }

        # operation successed
        return response(
            data=dict(self.model.db.items() + realtime_data.items()))


if __name__ == "__main__":
    from sanji.connection.mqtt import Mqtt
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    _logger = logging.getLogger("sanji.time")
    index = Index(connection=Mqtt())
    index.start()

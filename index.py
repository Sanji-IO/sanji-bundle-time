#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from sanji.core import Sanji
from sanji.core import Route
from systime.ntp import Ntp
from systime.systime import SysTime

_logger = logging.getLogger("sanji.time")


class Index(Sanji):

    def init(self, *args, **kwargs):
        self.config = {
            "timezone": "+08:00,0",
            "ntp": {
                "enable": 0,
                "servers": ["pool.ntp.org"],
                "interval": 3600
            }
        }
        self.ntp = Ntp(self.config["ntp"])

    @Route(methods="get", resource="/system/time")
    def get(self, message, response):
        realtime_data = {
            "time": SysTime.get_system_time()
        }

        return response(data=dict(self.config.items() + realtime_data.items()))

    @Route(methods="put", resource="/system/time")
    def put(self, message, response):
        rc = None
        try:
            # change timezone
            if "timezone" in message.data:
                rc = SysTime.set_system_timezone(message.data["timezone"])
                if rc is False:
                    raise RuntimeWarning("Change timezone failed.")
                self.config["timezone"] = message.data["timezone"]

            # manual change sys time
            if "time" in message.data:
                rc = SysTime.set_system_time(message.data["time"])
                if rc is False:
                    raise RuntimeWarning("Change system time failed.")

            # update ntp settings
            if "ntp" in message.data:
                rc = self.ntp.update(message.data["ntp"])
                if rc is False:
                    raise RuntimeWarning("Update ntp settings failed.")
                self.config["ntp"] = dict(self.config["ntp"].items()
                                          + message.data["ntp"].items())

            if rc is None:
                return response(code=400,
                                data={"message": "No input paramters."})
        except Exception as e:
            code = 400 if not isinstance(e, RuntimeWarning) else 500
            return response(code=code, data={"message": str(e)})

        realtime_data = {
            "time": SysTime.get_system_time()
        }

        # operation successed
        return response(data=dict(self.config.items() + realtime_data.items()))

if __name__ == "__main__":
    from sanji.connection.mqtt import Mqtt
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    _logger = logging.getLogger("sanji.time")
    index = Index(connection=Mqtt())
    index.start()

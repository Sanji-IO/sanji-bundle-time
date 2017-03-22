#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import subprocess
from datetime import datetime
import dateutil.tz as tz


class SysTime(object):

    ZONEINFO_PATH = "/usr/share/zoneinfo"
    ZONETAB_PATH = "{}/zone.tab".format(ZONEINFO_PATH)
    ISO3166TAB_PATH = "{}/iso3166.tab".format(ZONEINFO_PATH)

    @staticmethod
    def get_system_time():
        return datetime.now(tz.tzlocal()).strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    @staticmethod
    def set_system_time(time_string):
        """
        time_string should be iso 8601 time
        Exception:
            ValueError if time format is wrong
        """
        rc = None
        try:
            dateTimeString = datetime\
                .strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")\
                .strftime("%m%d%H%M%Y")

        except ValueError:
            raise ValueError('Time format error.')

        else:
            rc = subprocess.call(
                "date --utc %s; hwclock -w" % dateTimeString, shell=True)

        return True if rc == 0 else False

    @staticmethod
    def get_system_timezone_list():
        """
        return timezone list
        """
        # list zone.tab
        zonetab = []
        with open(SysTime.ZONETAB_PATH, "rb") as f:
            for line in f:
                if not line.startswith("#"):
                    zone = line.rstrip().split("\t")
                    zonetab.append({"cca2": zone[0], "name": zone[2]})

        # list iso3166.tab
        iso3166tab = []
        with open(SysTime.ISO3166TAB_PATH, "rb") as f:
            for line in f:
                if not line.startswith("#"):
                    zone = line.rstrip().split("\t")
                    iso3166tab.append({"cca2": zone[0], "name": zone[1]})

        return {"zone": zonetab, "iso3166": iso3166tab}

    @staticmethod
    def set_system_timezone(timezone):
        """
        timezone should be existed in /usr/share/zoneinfo
        Exception:
            ValueError if timezone sting is wrong
        """
        if os.path.isfile("{}/{}".format(SysTime.ZONEINFO_PATH, timezone)):
            rc = subprocess.call("echo \"%s\" > /etc/timezone;" %
                                 timezone +
                                 "dpkg-reconfigure -f noninteractive tzdata",
                                 shell=True)

        else:
            raise ValueError('Timezone not exist.')

        return True if rc == 0 else False

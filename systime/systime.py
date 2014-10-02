#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess
from datetime import datetime


class Time(object):

    TIMEZONE = {
        "-11:00,0": "Pacific/Samoa",               # SST
        "-10:00,0": "US/Hawaii",                   # HST
        "-09:00,1": "US/Alaska",                   # AKDT
        "-08:00,1": "Pacific",                     # PDT
        "-07:00,0": "US/Arizona",                  # MST
        "-07:00,1": "US/Mountain",                 # MDT
        "-06:00,0": "Canada/Saskatchewan",         # CST
        "-06:00,1": "US/Central",                  # CDT
        "-05:00,0": "America/Bogota",              # COT
        "-05:00,1": "US/Eastern",                  # EDT
        "-04:00,1": "America/Manaus",              # AMT
        "-04:00,0": "America/Caracas",             # VET
        "-03:30,1": "Canada/Newfoundland",         # NDT
        "-03:00,1": "America/Montevideo",          # UYT
        "-03:00,0": "right/America/Buenos_Aires",  # ART
        "-02:00,1": "America/Noronha",             # FNT
        "-01:00,1": "Atlantic/Azores",             # AZOST
        "-01:00,0": "Atlantic/Cape_Verde",         # CVT
        "-00:00,0": "Africa/Casablanca",           # WET
        "-00:00,1": "Europe/London",               # BST
        "+01:00,1": "Europe/Amsterdam",            # CEST
        "+01:00,0": "Africa/Gaborone",             # CAT    +02:00??
        "+02:00,1": "Asia/Amman",                  # EET    +02:00??
        "+02:00,0": "Africa/Harare",               # CAT    +02:00??
        "+03:00,1": "Asia/Baghdad",                # AST
        "+03:00,0": "Asia/Kuwait",                 # AST
        "+03:30,0": "Asia/Tehran",                 # IRDT
        "+04:00,0": "Asia/Muscat",                 # GST
        "+04:00,1": "Asia/Baku",                   # AZST
        "+04:30,0": "Asia/Kabul",                  # AFT
        "+05:00,1": "Asia/Oral",                   # ORAT
        "+05:00,0": "Asia/Karachi",                # PKT
        "+05:30,0": "Asia/Kolkata",                # IST
        "+05:45,0": "Asia/Katmandu",               # NPT
        "+06:00,0": "Asia/Dhaka",                  # BDT
        "+06:00,1": "Asia/Almaty",                 # ALMT
        "+06:30,0": "Asia/Rangoon",                # MMT
        "+07:00,1": "Asia/Krasnoyarsk",            # KRAST
        "+07:00,0": "Asia/Bangkok",                # ICT
        "+08:00,0": "Asia/Taipei",                 # CST
        "+08:00,1": "Asia/Irkutsk",                # IRKST
        "+09:00,1": "Asia/Yakutsk",                # YAKST
        "+09:00,0": "Asia/Tokyo",                  # JST
        "+09:30,0": "Australia/Darwin",            # CST
        "+09:30,1": "Australia/Adelaide",          # CST
        "+10:00,0": "Australia/Brisbane",          # EST
        "+10:00,1": "Australia/Canberra",          # EST
        "+11:00,0": "Asia/Magadan",                # MAGST
        "+12:00,1": "Pacific/Auckland",            # NZDT
        "+12:00,0": "Pacific/Fiji",                # FJT
        "+13:00,0": "Pacific/Tongatapu",           # TOT
    }

    def __init__(self):
        self.config = {
            "timezone": "+08:00,0"
        }

    @staticmethod
    def get_system_time():
        return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

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
            dateTimeString = time_string

        except ValueError:
            raise ValueError('Time format error. ')

        else:
            rc = subprocess.call(
                "date %s; hwclock -w" % dateTimeString, shell=True)

        return True if rc == 0 else False

    def get_system_timezone(self):
        return self.config["timezone"]

    def set_system_timezone(self, tz_string):
        """
        tz_string should be listed in Time.TIMEZONE
        Exception:
            ValueError if timezone sting is wrong
        """
        if tz_string in Time.TIMEZONE:
            rc = subprocess.call("echo \"%s\" > /etc/timezone;" %
                                 Time.TIMEZONE[tz_string] +
                                 "dpkg-reconfigure -f noninteractive tzdata",
                                 shell=True)
            if rc == 0:
                self.config["timezone"] = tz_string

        else:
            raise ValueError('Timezone string error.')

        return True if rc == 0 else False

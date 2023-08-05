#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2014 Martin Raspaud

# Author(s):

#   Kristian Rune Larsen <krl@dmi.dk>
#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Trigger and region_collector test file

AVHR_HRP_00_M01_20141017122200Z_20141017122300Z_N_O_20141017122450Z.bz2  avhrr_20141016_130300_noaa19.hrp.bz2
SVMC_npp_d20141017_t1139095_e1140339_b15396_c20141017114526433119_eum_ops.h5.bz2 AVHR_xxx_1B_M02_20141017122203Z_20141017122503Z_N_O_20141017133010Z
"""

from trollduction.collectors import trigger
from trollduction.collectors import region_collector
from pyresample import utils
import json
import os
from datetime import datetime, timedelta


input_dirs = ['tests/data', ]

regions = [
    utils.load_area('/home/a001673/usr/src/satprod/etc/areas.def', 'scan1')]

timeliness = timedelta(days=7000)
collectors = [region_collector.RegionCollector(
    region, timeliness) for region in regions]

# DONE timeout not handled
# DONE (kinda) should be able to handle both inotify, database events or
# posttroll messages
# DONE metadata should be decoded.


def terminator(metadata):
    """Dummy terminator function.
    """
    print metadata


def read_granule_metadata(filename):
    """Read the json metadata from *filename*.
    """
    with open(filename) as jfp:
        metadata = json.load(jfp)[0]

    metadata['uri'] = "file://" + os.path.abspath(filename)

    for attr in ["start_time", "end_time"]:
        try:
            metadata[attr] = datetime.strptime(metadata[attr],
                                               "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            metadata[attr] = datetime.strptime(metadata[attr],
                                               "%Y-%m-%dT%H:%M:%S")
    return metadata

decoder = read_granule_metadata


granule_trigger = trigger.InotifyTrigger(collectors, terminator,
                                         decoder, input_dirs)

try:
    granule_trigger.loop()
    print "Thank you for using pytroll! See you soon on pytroll.org."
except KeyboardInterrupt:
    print "Thank you for using pytroll! See you soon on pytroll.org."

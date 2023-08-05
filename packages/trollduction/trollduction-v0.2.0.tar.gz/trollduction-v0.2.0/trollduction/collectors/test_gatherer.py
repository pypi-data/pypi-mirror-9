#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Martin Raspaud

# Author(s):

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

"""Test the gatherer.

sending pytroll:/HRPT/0 collection a001673@c20035.ad.smhi.se 2014-10-22T12:04:06.615031 v1.01 application/json [{"format": "HRPT", "start_time": "2014-10-22T11:40:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114000_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114000_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:41:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:43:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114300_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114300_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:44:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:42:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114200_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114200_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:43:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:41:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114100_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114100_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:42:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:44:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114400_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114400_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:45:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:46:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114600_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114600_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:47:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:45:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114500_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114500_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:46:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:47:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114700_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114700_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:48:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:48:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114800_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114800_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:49:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:49:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_114900_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_114900_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:50:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:50:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_115000_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_115000_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:51:00"}, {"format": "HRPT", "start_time": "2014-10-22T11:51:00", "level": "0", "number": "19", "uri": "/data/prod/satellit/ears/avhrr/avhrr_20141022_115100_noaa19.hrp.bz2", "platform": "noaa 19", "instrument": "avhrr", "duration": "60", "filename": "avhrr_20141022_115100_noaa19.hrp.bz2", "type": "binary", "end_time": "2014-10-22T11:52:00"}]



sending pytroll:/EOS_thinned/1B collection a001673@c20035.ad.smhi.se 2014-10-22T12:12:07.957108 v1.01 application/json [{"proc_time": "2014-10-22T11:32:33", "format": "EOS", "start_time": "2014-10-22T09:00:00", "level": "1B", "uri": "/data/prod/satellit/modis/lvl1/thin_MYD021KM.A2014295.0900.005.2014295113233.NRT.hdf", "filename": "thin_MYD021KM.A2014295.0900.005.2014295113233.NRT.hdf", "instrument": "modis", "platform": "aqua", "duration": "300", "type": "HDF4", "end_time": "2014-10-22T09:05:00"}, {"proc_time": "2014-10-22T11:32:17", "format": "EOS", "start_time": "2014-10-22T09:05:00", "level": "1B", "uri": "/data/prod/satellit/modis/lvl1/thin_MYD021KM.A2014295.0905.005.2014295113217.NRT.hdf", "filename": "thin_MYD021KM.A2014295.0905.005.2014295113217.NRT.hdf", "instrument": "modis", "platform": "aqua", "duration": "300", "type": "HDF4", "end_time": "2014-10-22T09:10:00"}, {"proc_time": "2014-10-22T11:31:29", "format": "EOS", "start_time": "2014-10-22T09:10:00", "level": "1B", "uri": "/data/prod/satellit/modis/lvl1/thin_MYD021KM.A2014295.0910.005.2014295113129.NRT.hdf", "filename": "thin_MYD021KM.A2014295.0910.005.2014295113129.NRT.hdf", "instrument": "modis", "platform": "aqua", "duration": "300", "type": "HDF4", "end_time": "2014-10-22T09:15:00"}]





{'proctime': datetime.datetime(2014, 10, 22, 11, 46, 41, 434131), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 38, 26, 400000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1138264_e1139506_b15466_c20141022114641434131_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 39, 50, 600000), 'filename': 'SVMC_npp_d20141022_t1138264_e1139506_b15466_c20141022114641434131_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 48, 45, 740119), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 42, 42, 600000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1142426_e1144068_b15466_c20141022114845740119_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 44, 6, 800000), 'filename': 'SVMC_npp_d20141022_t1142426_e1144068_b15466_c20141022114845740119_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 52, 20, 287180), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 39, 51, 800000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1139518_e1141160_b15466_c20141022115220287180_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 41, 16), 'filename': 'SVMC_npp_d20141022_t1139518_e1141160_b15466_c20141022115220287180_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 53, 38, 536125), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 44, 8), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1144080_e1145322_b15466_c20141022115338536125_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 45, 32, 200000), 'filename': 'SVMC_npp_d20141022_t1144080_e1145322_b15466_c20141022115338536125_eum_ops.h5.bz2', 'type': 'hdf5'}
INFO:trollduction.collectors.region_collector:Added suomi npp (2014-10-22 11:44:08) granule to area euron1
DEBUG:trollduction.collectors.region_collector:Predicting granules covering euron1
INFO:trollduction.collectors.region_collector:Planned granules: [datetime.datetime(2014, 10, 22, 11, 44, 8), datetime.datetime(2014, 10, 22, 11, 45, 32, 100000), datetime.datetime(2014, 10, 22, 11, 46, 56, 200000), datetime.datetime(2014, 10, 22, 11, 48, 20, 300000), datetime.datetime(2014, 10, 22, 11, 49, 44, 400000), datetime.datetime(2014, 10, 22, 11, 51, 8, 500000), datetime.datetime(2014, 10, 22, 11, 52, 32, 600000), datetime.datetime(2014, 10, 22, 11, 53, 56, 700000)]
INFO:trollduction.collectors.region_collector:Planned timeout: 2014-10-22T12:10:20.800000


{'proctime': datetime.datetime(2014, 10, 22, 11, 54, 57, 981127), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 48, 24, 200000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1148242_e1149484_b15466_c20141022115457981127_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 49, 48, 400000), 'filename': 'SVMC_npp_d20141022_t1148242_e1149484_b15466_c20141022115457981127_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 53, 40, 982119), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 45, 33, 400000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1145334_e1146576_b15466_c20141022115340982119_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 46, 57, 600000), 'filename': 'SVMC_npp_d20141022_t1145334_e1146576_b15466_c20141022115340982119_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 57, 2, 927128), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 46, 58, 800000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1146588_e1148230_b15466_c20141022115702927128_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 48, 23), 'filename': 'SVMC_npp_d20141022_t1146588_e1148230_b15466_c20141022115702927128_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 52, 23, 992123), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 41, 17, 200000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1141172_e1142414_b15466_c20141022115223992123_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 42, 41, 400000), 'filename': 'SVMC_npp_d20141022_t1141172_e1142414_b15466_c20141022115223992123_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 58, 51, 809124), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 51, 15), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1151150_e1152392_b15466_c20141022115851809124_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 52, 39, 200000), 'filename': 'SVMC_npp_d20141022_t1151150_e1152392_b15466_c20141022115851809124_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 12, 2, 36, 490150), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 52, 40, 400000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1152404_e1154046_b15466_c20141022120236490150_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 54, 4, 600000), 'filename': 'SVMC_npp_d20141022_t1152404_e1154046_b15466_c20141022120236490150_eum_ops.h5.bz2', 'type': 'hdf5'}

{'proctime': datetime.datetime(2014, 10, 22, 11, 58, 9, 287119), 'format': 'SDR', 'start_time': datetime.datetime(2014, 10, 22, 11, 49, 49, 600000), 'level': '1B', 'orbit_number': 15466, 'instrument': 'viirs', 'uri': '/data/prod/satellit/ears/viirs/SVMC_npp_d20141022_t1149496_e1151138_b15466_c20141022115809287119_eum_ops.h5.bz2', 'platform': 'suomi npp', 'end_time': datetime.datetime(2014, 10, 22, 11, 51, 13, 800000), 'filename': 'SVMC_npp_d20141022_t1149496_e1151138_b15466_c20141022115809287119_eum_ops.h5.bz2', 'type': 'hdf5'}

"""

import unittest
from trollduction.collectors.gatherer import get_metadata
from datetime import datetime


class TestGatherer(unittest.TestCase):

    def test_metadata(self):
        ears_avhrr = {'platform': 'noaa',
                      'end_time': datetime(2014, 10, 16, 13, 4),
                      'format': 'HRPT',
                      'duration': '60',
                      'pattern': 'avhrr_{start_time:%Y%m%d_%H%M%S}_{platform:4s}{number:2s}.hrp.bz',
                      'start_time': datetime(2014, 10, 16, 13, 3),
                      'type': 'binary',
                      'number': '19'}
        self.assertEquals(ears_avhrr,
                          get_metadata("avhrr_20141016_130300_noaa19.hrp.bz"))

        ears_metop = {'proc_time': datetime(2014, 10, 17, 12, 24, 50),
                      'level': '00',
                      'pattern': 'AVHR_HRP_{level:2s}_{platform:1s}{number:2s}_{start_time:%Y%m%d%H%M%S}Z_{end_time:%Y%m%d%H%M%S}Z_N_O_{proc_time:%Y%m%d%H%M%S}Z.bz2',
                      'start_time': datetime(2014, 10, 17, 12, 22),
                      'format': 'AHRPT',
                      'number': '01',
                      'platform': 'M',
                      'end_time': datetime(2014, 10, 17, 12, 23),
                      'type': 'binary'}
        self.assertEquals(ears_metop, get_metadata(
            "AVHR_HRP_00_M01_20141017122200Z_20141017122300Z_N_O_20141017122450Z.bz2"))

        gds_metop = {'proc_time': datetime(2014, 10, 17, 13, 30, 10),
                     'level': '1B',
                     'pattern': 'AVHR_xxx_{level:2s}_{platform:1s}{number:2s}_{start_time:%Y%m%d%H%M%S}Z_{end_time:%Y%m%d%H%M%S}Z_N_O_{proc_time:%Y%m%d%H%M%S}Z',
                     'start_time': datetime(2014, 10, 17, 12, 22, 3),
                     'format': 'EPS',
                     'number': '02',
                     'platform': 'M',
                     'end_time': datetime(2014, 10, 17, 12, 25, 3),
                     'type': 'PDS'}
        self.assertEquals(gds_metop,  get_metadata(
            "AVHR_xxx_1B_M02_20141017122203Z_20141017122503Z_N_O_20141017133010Z"))
        ears_viirs = {'proctime': datetime(2014, 10, 17, 11, 45, 26, 433119),
                      'level': '1B',
                      'pattern': 'SVMC_{platform:3s}_d{start_date:%Y%m%d}_t{start_time:%H%M%S%f}_e{end_time:%H%M%S%f}_b{orbit_number:5d}_c{proctime:%Y%m%d%H%M%S%f}_eum_ops.h5.bz2',
                      'start_time': datetime(1900, 1, 1, 11, 39, 9, 500000),
                      'format': 'SDR',
                      'orbit_number': 15396,
                      'platform': 'npp',
                      'end_time': datetime(1900, 1, 1, 11, 40, 33, 900000),
                      'type': 'hdf5',
                      'start_date': datetime(2014, 10, 17, 0, 0)}

        self.assertEquals(ears_viirs, get_metadata(
            'SVMC_npp_d20141017_t1139095_e1140339_b15396_c20141017114526433119_eum_ops.h5.bz2'))

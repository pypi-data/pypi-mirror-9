# -*- coding: utf-8 -*-
###############################################################################
#    Mobile Map Downloader - Download maps for your mobile phone.             #
#                                                                             #
#    Copyright (C) 2014 by Eike Welk                                          #
#    eike.welk@gmx.net                                                        #
#                                                                             #
#    License: GPL Version 3                                                   #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
###############################################################################
"""
Test the download functions.
"""

from __future__ import division
from __future__ import absolute_import              

#For test modules: ----------------------------------------------------------
#import pytest #contains `skip`, `fail`, `raises`, `config`

import time
import os.path as path
from pprint import pprint


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


def relative_path(*path_comps):
    "Create file paths that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))

    
def test_OsmandInstaller_name_conversion():
    """OpenandromapsManager: Test the name conversion functions."""
    from mob_map_dl.install import OsmandInstaller
    
    print "Start."
    device_path = relative_path("../../test_data/TEST-DEVICE1")
    d1 = "osmand/Jamaica_centralamerica_2.obf"
    d2 = "osmand/Monaco_europe_2.obf"
    f1 = path.join(device_path, "osmand/Jamaica_centralamerica_2.obf")
    f2 = path.join(device_path, "osmand/Monaco_europe_2.obf")
    
    mgr = OsmandInstaller(device_path)
    
    assert mgr.make_disp_name(f1) == d1
    assert mgr.make_disp_name(f2) == d2
    assert mgr.make_full_name(d1) == f1
    assert mgr.make_full_name(d2) == f2


def test_OsmandInstaller_get_file_list():
    "OsmandInstaller: Get list of installed maps."
    from mob_map_dl.install import OsmandInstaller   
    
    print "Start."
    device_path = relative_path("../../test_data/TEST-DEVICE1")
    
    i = OsmandInstaller(device_path)
    l = i.get_file_list()
    
    pprint(l)
    assert len(l) == 2
    assert l[0].disp_name == 'osmand/Jamaica_centralamerica_2.obf'
    assert l[0].size == 4518034
    assert l[1].disp_name == "osmand/Monaco_europe_2.obf"
    assert l[1].size == 342685

    
def test_OruxmapsInstaller_name_conversion():
    """OpenandromapsManager: Test the name conversion functions."""
    from mob_map_dl.install import OruxmapsInstaller
    
    print "Start."
    device_path = relative_path("../../test_data/TEST-DEVICE1")
    d1 = "oam/SouthAmerica_bermuda"
    d2 = "oam/europe_France_South"
    d3 = "project/country_name"
    f1 = path.join(device_path, "oruxmaps/mapfiles/oam_SouthAmerica_bermuda.map")
    f2 = path.join(device_path, "oruxmaps/mapfiles/oam_europe_France_South.map")
    f3 = path.join(device_path, "oruxmaps/mapfiles/project_country_name.map")
    
    mgr = OruxmapsInstaller(device_path)
    
    assert mgr.make_disp_name(f1) == d1
    assert mgr.make_disp_name(f2) == d2
    assert mgr.make_disp_name(f3) == d3
    assert mgr.make_full_name(d1) == f1
    assert mgr.make_full_name(d2) == f2
    assert mgr.make_full_name(d3) == f3


def test_OruxmapsInstaller_get_file_list():
    "OsmandInstaller: Get list of installed maps."
    from mob_map_dl.install import OruxmapsInstaller   
    
    print "Start."
    device_path = relative_path("../../test_data/TEST-DEVICE1")
    
    i = OruxmapsInstaller(device_path)
    l = i.get_file_list()
    
    pprint(l)
    assert len(l) == 1
    assert l[0].disp_name == "oam/SouthAmerica_bermuda"
    assert l[0].size == 447481
    

if __name__ == "__main__":
#    test_OsmandInstaller_name_conversion()
#    test_OsmandInstaller_get_file_list()
    test_OruxmapsInstaller_name_conversion()
#    test_OruxmapsInstaller_get_file_list()
    
    pass #IGNORE:W0107

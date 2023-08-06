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
import os
import shutil
from pprint import pprint
import datetime


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


def relative_path(*path_comps):
    "Create file paths that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))

def create_writable_test_dirs(idx):
    """
    Create temporary writable directories with test data. Different names 
    for each test enable parallel execution of tests.
    
    The following directories are created:
    
    "../../test_tmp/mob_map_dl" + idx 
        Application directory with test data.
        
    "../../test_tmp/TEST-DEVICE" + idx
        Device directory  with test data.
    """
    idx = str(idx)
    test_app_dir = relative_path("../../test_tmp/mob_map_dl" + idx)
    test_dev_dir = relative_path("../../test_tmp/TEST-DEVICE" + idx)
    shutil.rmtree(test_app_dir, ignore_errors=True)
    shutil.rmtree(test_dev_dir, ignore_errors=True)
    shutil.copytree(relative_path("../../test_data/maps"), test_app_dir)
    shutil.copytree(relative_path("../../test_data/TEST-DEVICE1"), test_dev_dir)
    return test_app_dir, test_dev_dir

#def download_test_data():
#    "Download some test data"
#    #    #File size 0.2 MiB
#    from mob_map_dl.download import OsmandDownloader
#    d = OsmandDownloader()
#    srvname = "http://download.osmand.net/download.php?standard=yes&file=Monaco_europe_2.obf.zip"
#    locname = relative_path("../../test_data/maps/osmand/Monaco_europe_2.obf.zip")
#    d.download_file(srvname, locname, "osmand/Monaco_europe_2")
#    #File size 3.0 MiB
#    srvname = "http://download.osmand.net/download.php?standard=yes&file=Jamaica_centralamerica_2.obf.zip"
#    locname = relative_path("../../test_data/maps/osmand/Jamaica_centralamerica_2.obf.zip")
#    d.download_file(srvname, locname, "osmand/Jamaica_centralamerica_2")


def test_OsmandManager_name_conversion():
    """OpenandromapsManager: Test the name conversion functions."""
    from mob_map_dl.local import OsmandManager
    
    print "Start."
    test_app_dir, _ = create_writable_test_dirs("l4")
    d1 = "osmand/europe_France_North.obf"
    d2 = "osmand/asia_Kazakhstan.obf"
    f1 = path.join(test_app_dir, "osmand/europe_France_North.obf.zip")
    f2 = path.join(test_app_dir, "osmand/asia_Kazakhstan.obf.zip")
    
    mgr = OsmandManager(test_app_dir)
    
    assert mgr.make_disp_name(f1) == d1
    assert mgr.make_disp_name(f2) == d2
    assert mgr.make_full_name(d1) == f1
    assert mgr.make_full_name(d2) == f2
    
    
def test_OsmandManager_get_file_list():
    "Test class OsmandManager: Extracting maps from downloaded archives."

    from mob_map_dl.local import OsmandManager
    download_dir = relative_path("../../test_data/maps/")
    
    m = OsmandManager(download_dir)
    l = m.get_file_list()
    
    pprint(l)
    assert len(l) == 2
    assert l[0].disp_name == "osmand/Jamaica_centralamerica_2.obf"
    assert l[1].disp_name == "osmand/Monaco_europe_2.obf"


def test_OsmandManager_get_map_extractor():
    """
    OsmandManager: Create an object that extracts a map from one of the 
    downloaded *.zip files.
    """
    from mob_map_dl.local import OsmandManager
    
    download_dir = relative_path("../../test_data/maps/osmand/")
    map_path = relative_path("../../test_data/maps/osmand/Jamaica_centralamerica_2.obf.zip")
    
    m = OsmandManager(download_dir)
    fzip, size_total, mod_time = m.get_map_extractor(map_path)
    buf = fzip.read()
    
    print "len(buf):", len(buf)
    print "size_total:", size_total
    print "mod_time:", mod_time
    assert len(buf) == 4518034
    assert len(buf) == size_total
    assert mod_time == datetime.datetime(2014, 8, 3, 15, 10, 2)


def test_OsmandManager_extract_map():
    "Test class OsmandManager: Extracting maps from downloaded archives."
    from mob_map_dl.local import OsmandManager
    
    print "Start prepare map."
    test_app_dir, test_dev_dir = create_writable_test_dirs("l3")
    inp_name = path.join(test_app_dir, "osmand/Jamaica_centralamerica_2.obf.zip")
    out_name = path.join(test_dev_dir, "osmand/Jamaica_centralamerica_2.obf")
    os.remove(out_name)
    
    m = OsmandManager(test_app_dir)
    m.extract_map(inp_name, out_name, "osmand/Jamaica_centralamerica_2")
    
    #Test name and size of extracted file
    assert path.isfile(out_name)
    file_size = path.getsize(out_name)
    print "file size [MiB]:", file_size / 1024**2
    assert file_size == 4518034


def test_OpenandromapManager_name_conversion():
    """OpenandromapsManager: Test the name conversion functions."""
    from mob_map_dl.local import OpenandromapsManager
    
    print "Start."
    test_app_dir, _ = create_writable_test_dirs("l4")
    d1 = "oam/europe_France_North"
    d2 = "oam/asia_Kazakhstan"
    f1 = path.join(test_app_dir, "oam/europe_France_North.zip")
    f2 = path.join(test_app_dir, "oam/asia_Kazakhstan.zip")
    
    mgr = OpenandromapsManager(test_app_dir)
    
    assert mgr.make_disp_name(f1) == d1
    assert mgr.make_disp_name(f2) == d2
    assert mgr.make_full_name(d1) == f1
    assert mgr.make_full_name(d2) == f2
    
    
def test_OpenandromapManager_get_map_extractor():
    """OpenandromapsManager: Test the name conversion functions."""
    from mob_map_dl.local import OpenandromapsManager
    
    print "Start."
    test_app_dir, _ = create_writable_test_dirs("l5")
#    arch_path = path.join(test_app_dir, "oam/usa_Yellowstone_NP.zip")
    arch_path = path.join(test_app_dir, "oam/SouthAmerica_bermuda.zip")
    
    mgr = OpenandromapsManager(test_app_dir)
    fzip, size_total, _ = mgr.get_map_extractor(arch_path)
    map_content = fzip.read()
    
    size_mib = len(map_content) / 1024**2
    print "size:", size_mib, "Mib"
    assert 0.4 < size_mib < 0.6
    assert size_total == len(map_content)


if __name__ == "__main__":
    test_OsmandManager_name_conversion()
#    test_OsmandManager_get_file_list()
#    test_OsmandManager_get_map_extractor()
#    test_OsmandManager_extract_map()
#    test_OpenandromapManager_name_conversion()
#    test_OpenandromapManager_get_map_extractor()
    
    pass #IGNORE:W0107

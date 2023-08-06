# -*- coding: utf-8 -*-
###############################################################################
#    Mobile Map Downloader - Download maps for your mobile phone.             #
#                                                                             #
#    Copyright (C) 2015 by Eike Welk                                          #
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
import os
import os.path as path
import shutil
from pprint import pprint
import urllib2


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


def relative_path(*path_comps):
    "Create file paths that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))

def find_index(list_like, search_val, key=lambda x:x):
    """
    Find the index of an element in a list like container. 
    
    Accepts a custom function to compute the comparison key, like ``list.sort``.
    
    Returns
    --------
    
    int | NoneType: Index of found element or ``None`` if no element is found.
    
    TODO: Write unit test.
    """
    for i, elem in enumerate(list_like):
        comp_val = key(elem)
        if comp_val == search_val:
            return i 
    else:
        return None
    
    
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


def test_find_index():
    "Test internal helper function ``find_index``."
    
    l = ["the foo", "the bar", "the baz", "the boo"]
    def slice_47(s):
        return s[4:7]

    idx = find_index(l, "bar", slice_47)
    assert idx == 1

    idx = find_index(l, "moo", slice_47)
    assert idx is None


def test_BaseDownloader_download_file():
    "Test class BaseDownloader: Downloading of files from a server on the Internet."
    from mob_map_dl.download import BaseDownloader
    
    print "Start download_file"
    test_map_name = relative_path("../../test_tmp/test_1.obf.zip")
    try: os.remove(test_map_name)
    except OSError: pass
    assert not path.exists(test_map_name)
    
    #File size 0.2 MiB
    url = "http://download.osmand.net/download.php?standard=yes&file=Monaco_europe_2.obf.zip"
#    #File size 3.0 MiB
#    url = "http://download.osmand.net/download.php?standard=yes&file=Jamaica_centralamerica_2.obf.zip"
    
    d = BaseDownloader()
    d.download_file(url, test_map_name, "test-file-name.foo")
    
    #Test name and size of downloaded file
    #The actual file size will vary with each revision of the map.
    assert path.isfile(test_map_name)
    file_size = path.getsize(test_map_name)/1024**2
    print "file size [MiB]:", file_size
    assert 0.2 < file_size < 0.5
    
    
def test_OsmandDownloader_get_file_list():
    "Test class OsmandDownloader: Listing of files that can be downloaded."
    from mob_map_dl.download import OsmandDownloader
    
    print "Start get_file_list"
    d = OsmandDownloader()
    l = d.get_file_list()
    
    pprint(l)
    print len(l)
    
    #Test if some files exist
    get_disp_name = lambda e: e.disp_name
    assert find_index(l, "osmand/France_rhone-alpes_europe_2.obf", 
                      key=get_disp_name) is not None
    assert find_index(l, "osmand/Germany_nordrhein-westfalen_europe_2.obf", 
                      key=get_disp_name) is not None
    assert find_index(l, "osmand/Jamaica_centralamerica_2.obf", 
                      key=get_disp_name) is not None
    assert find_index(l, "osmand/Monaco_europe_2.obf", 
                      key=get_disp_name) is not None
    #Test the names of first & last file
    assert l[0].disp_name == "osmand/Afghanistan_asia_2.obf"
    assert l[-1].disp_name == "osmand/Zimbabwe_africa_2.obf"
    #Number of files must be in certain range.
    assert 500 < len(l) < 600
        
    #Test if the extracted URLs are correct
    idx = find_index(l, "osmand/Monaco_europe_2.obf", get_disp_name)
    url = l[idx].full_name
    fsrv = urllib2.urlopen(url)
    map_zip = fsrv.read()
    len_mib = len(map_zip) / 1024**2
    print len(map_zip), "B", len_mib, "MiB", round(len_mib, 1), "MiB rounded"
    assert 0.2 < len_mib < 0.5

    
def test_OsmandDownloader_chaching_mechanism():
    """
    Test the caching mechanism with ``OpenandromapsDownloader``.
    
    The caching mechanism is really built into ``BaseDownloader``, however
    it must be tested with a complete downloader class, that has a functioning 
    implementation of ``get_file_list``.
    
    We use ``OsmandDownloader`` for the test because it is fairly fast.
    Actually downloading the and parsing the HTML is nearly as fast (0.3 s) 
    than un-pickling the cached list (0.05 s). The test may fail on a computer 
    with a really fast Internet connection. 
    
    The caching mechanism is intended for ``OpenandromapsDownloader``, which
    needs several seconds to download and parse the HTML, because the server 
    answers with several 100 Kib of HTML.
    """
    from mob_map_dl.download import OsmandDownloader
    
    print "Start"
    app_dir, _ = create_writable_test_dirs("d1")
    cache_time = 2
    
    dl = OsmandDownloader(app_dir, cache_time)
    
    #Download list, parse HTML, write cache file, should take long.
    t0 = time.time()
    _ = dl.get_file_list()
    t1 = time.time()
    delta1 = t1 - t0 
    print "Get file list, 1st time:", delta1, "s"
    
    #Now return cached list, should take short time.
    _ = dl.get_file_list()
    t2 = time.time()
    delta2 = t2 - t1
    print "Get file list, 2nd time:", delta2, "s"
    assert delta2 < delta1
    assert delta2 < 0.1
    
    print "Sleeping..."
    time.sleep(cache_time)
    
    #Cache is expired, now it should take long again.
    t3 = time.time()
    _ = dl.get_file_list()
    t4 = time.time()
    delta4 = t4 - t3
    print "Get file list, after sleep:", delta4, "s"
    assert delta4 > delta2
    assert abs(delta1 - delta4) < 0.15
    

def test_OpenandromapsDownloader_make_disp_name():
    from mob_map_dl.download import OpenandromapsDownloader
    
    print "Start"
    down = OpenandromapsDownloader()

    u1 = "http://www.openandromaps.org/maps/Germany/Germany_Mid_hike.zip"
    u2 = "http://www.openandromaps.org/maps/europe/France_North.zip"
    n1 = "oam/Germany_Germany_Mid_hike" 
    n2 = "oam/europe_France_North"
    
    n = down.make_disp_name(u1)
    assert n == n1
    
    n = down.make_disp_name(u2)
    assert n == n2


def test_OpenandromapsDownloader_get_file_list():
    from mob_map_dl.download import OpenandromapsDownloader
    
    print "Start"
    down = OpenandromapsDownloader()

    l = down.get_file_list()
    
    pprint(l)
    print len(l)
    
    #Number of files must be in certain range.
    assert 200 < len(l) < 250
    #Test if some files exist. One file from each HTML page.
    get_disp_name = lambda e: e.disp_name
    assert find_index(l, "oam/europe_France_South", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/Germany_Germany_Mid_hike", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/Russia_Central", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/usa_California", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/canada_Saskatchewan", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/SouthAmerica_Mexico", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/oceania_NewZealand", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/asia_Kazakhstan", 
                      key=get_disp_name) is not None
    assert find_index(l, "oam/africa_kenya", 
                      key=get_disp_name) is not None
    
    #Test if the extracted URLs are correct, (2 MiB download)
    idx = find_index(l, "oam/SouthAmerica_bermuda", get_disp_name)
    url = l[idx].full_name
    fsrv = urllib2.urlopen(url)
    map_zip = fsrv.read()
    len_mib = len(map_zip) / 1024**2
    print len(map_zip), "B", len_mib, "MiB", round(len_mib, 1), "MiB rounded"
    #Test rough dimensions, exact size changes with every new revision
    assert 1.8 < len_mib < 3.0


if __name__ == "__main__":
#    test_BaseDownloader_download_file()
#    test_OsmandDownloader_get_file_list()
    test_OsmandDownloader_chaching_mechanism()
#    test_OpenandromapsDownloader_make_disp_name()
#    test_OpenandromapsDownloader_get_file_list()
    
    pass #IGNORE:W0107

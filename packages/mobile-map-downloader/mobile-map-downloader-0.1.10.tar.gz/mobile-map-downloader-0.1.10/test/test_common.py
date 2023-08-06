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
Test the ``common`` module.
"""

from __future__ import division
from __future__ import absolute_import              

#For test modules: ----------------------------------------------------------
#import pytest #contains `skip`, `fail`, `raises`, `config`

import time
import os
import os.path as path
#from pprint import pprint


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


def relative_path(*path_comps):
    "Create file paths that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))


def test_TextProgressBar():
    """
    Test class TextProgressBar
    """
    from mob_map_dl.common import TextProgressBar
    
    print "Start"
    pb = TextProgressBar("Foo: 42 bar", 42)
    for v in range(0, 42, 10):
        pb.update_val(v)
        time.sleep(1)
    pb.update_final(42, "Finished")


def test_items_sorted():
    """Test function items_sorted"""
    from mob_map_dl.common import items_sorted
    
    d = {"b":2, "a":1, "d":4, "c":3}
    print d
    ds = items_sorted(d)
    print ds
    
    assert ds[0] == ("a", 1)
    assert ds[1] == ("b", 2)
    assert ds[2] == ("c", 3)
    assert ds[3] == ("d", 4)


def test_PartFile():
    from mob_map_dl.common import PartFile
    
    print "Start"
    test_file = relative_path("../../test_tmp/test_PartFile.txt")
    if path.exists(test_file):
        os.remove(test_file)
    
    #No file with final name exists.
    f = PartFile(test_file, "wb")
    
    assert path.exists(test_file + ".part")
    
    f.write("foobar")
    f.close()
    
    assert path.exists(test_file)
    assert not path.exists(test_file + ".part")
    assert open(test_file).read() == "foobar"
    
    #File with final name exist (from last test)
    f = PartFile(test_file, "wb")
    
    assert path.exists(test_file + ".part")
    
    f.write("Boozalam!")
    f.close()
    
    assert path.exists(test_file)
    assert not path.exists(test_file + ".part")
    assert open(test_file).read() == "Boozalam!"
    
    
if __name__ == "__main__":
#    test_TextProgressBar()
#    test_items_sorted()
    test_PartFile()
    
    pass #IGNORE:W0107

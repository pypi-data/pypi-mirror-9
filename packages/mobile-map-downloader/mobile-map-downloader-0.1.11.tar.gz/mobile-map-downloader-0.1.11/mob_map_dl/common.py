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
Common functionality for all modules.
"""

from __future__ import division
from __future__ import absolute_import              

import time
from collections import namedtuple
import sys
import os
import os.path as path
import platform


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


VERSION = "0.1.11"
#Version of the program


MapMeta = namedtuple("MapMeta", 
                     "disp_name, full_name, size, time, description, map_type")
#Some meta data about each map
#    map_type: "osmand" | "mapsforge"


class TextProgressBar(object):
    """
    A progress bar for the console.
    
    Displays changing values on the console without creating a new line.
    The final update creates a new line.
    
    Update the value by calling: ``update_val``
    For the final update call: ``update_final``
    """
    def __init__(self, text, val_max, display_percent=True):
        """
        text: str
            Constant text, for example a file name. 
            
        val_max: int | float
            Maximum value, used for computing percent.
            
        display_percent: bool
            Display the value as percent, or as absolute value.
        """
        self.text = text
        self.val_max = val_max
        self.display_percent = display_percent
        self.num_backspace = 0
        #Length of last line that was printed on the console. 
        #(Number of necessary backspace characters.)
        self.anim_frames = "\|/-"
        self.anim_frame_i = 0
    
    def format_val(self, value):
        """
        Format the value as needed.
        """
        if self.display_percent:
            val_proc = value / self.val_max * 100
            val_msg = "{:3.1f}%".format(val_proc)
        else:
            val_msg = "{}".format(value)
        return val_msg
    
    def update_val(self, value):
        """
        Update the progress bar with new value
        """
        val_msg = self.format_val(value)
            
        self.anim_frame_i = (self.anim_frame_i + 1) % len(self.anim_frames)
        anim_frame=self.anim_frames[self.anim_frame_i]
        
        msg = "{text} - {val}  [{anim}]".format(
                                text=self.text, val=val_msg, anim=anim_frame)
        
        print chr(8) * self.num_backspace + msg,
        sys.stdout.flush()
        self.num_backspace = len(msg) + 1
            
    def update_final(self, value, final_text):
        """
        Create last update with newline.
        The ``final_text`` is printed at the end of the line.
        """
        val_msg = self.format_val(value)
        msg = "{text} - {val} - {fin}".format(
                                text=self.text, val=val_msg, fin=final_text)
        print chr(8) * self.num_backspace + msg
        
        self.num_backspace = None
        self.anim_frame_i = None
        
        
def items_sorted(in_dict):
    """
    Create ``list`` or (key, value) pairs, from the contents of ``in_dict``.
    The list is sorted by the dict's key.
    """
    items = in_dict.items()
    items.sort(key=lambda i: i[0])
    return items


class PartFile(file):
    """
    Self renaming "*.part" file.
    
    When the file is opened in the constructor a ".part" suffix is appended
    to the file name. When the file is closed the file is renamed to the 
    name that was passed in the constructor. 
    
    The constructor takes the same arguments as built in function ``open``.
    """
    def __init__(self, fname, *args):
        self.orig_name = fname
        file.__init__(self, fname + ".part", *args)
        
    def close(self):
        """
        Close the file and rename it to the original name, without the ".part"
        suffix.
        
        Details on writing to temporary file and renaming from Stackoverflow:
            http://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python
        """
        part_name = self.name
        self.flush()
#        os.fsync(self.fileno())  #Force write of file to disk.
        close_ret = file.close(self)
        
        #On windows renaming fails, if a file with the new name already exists.
        #    https://docs.python.org/2/library/os.html#os.rename
        if platform.system() == 'Windows' and path.exists(self.orig_name):
            os.remove(self.orig_name)
            
        os.rename(part_name, self.orig_name)
        return close_ret

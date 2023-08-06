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
Manage local files, that have previously been downloaded.
"""

from __future__ import division
from __future__ import absolute_import              

import time
import os
import fnmatch
from os import path
import zipfile
import datetime

from mob_map_dl.common import MapMeta, TextProgressBar, PartFile


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


class BaseManager(object):
    """
    Base class for local manager objects.
    """
    def __init__(self, _application_dir=None):
        """
        Object is initialized with the application's directory by top level, 
        computes its own sub-directory, and stores it.
        """
        self.download_dir = ""
        #Path to directory where the maps are stored. Is accessed by command: 
        # ``dlmap lsd -l`` 
    
    #--- Called by high level algorithms -------------------------------
    def make_disp_name(self, file_path):
        """Create canonical (display) name from path of map."""
        raise NotImplementedError()
        
    def make_full_name(self, disp_name):
        """Create path for map from its canonical (display) name."""
        raise NotImplementedError()
    
    def get_file_list(self):
        """
        Return a list of locally stored maps. 
        
        Return
        -------
        
        list[MapMeta]
        """
        raise NotImplementedError()
        
    def extract_map(self, arch_path, map_path, disp_name):
        """
        Extract a map from its downloaded archive.
        
        Relies on ``get_map_extractor`` which creates a file like object to
        extract the map from the archive. 
        
        Arguments
        ---------
        
        arch_path: str
            Path of the archive that contains the map.
        
        map_path: str
            Path where the extracted map should be stored. For example
            a mobile device's SD card.
        
        disp_name: str
            Canonical name of the map. Used in the progress bar.
        """
        fext = PartFile(map_path, "wb")
        fzip, size_total, _ = self.get_map_extractor(arch_path)
        
        size_mib = round(size_total / 1024**2, 1)
        msg = "{name} : {size} MiB".format(name=disp_name[0:50], size=size_mib)
        progress = TextProgressBar(msg, val_max=size_total)
        progress.update_val(0)
        
        buff_size = 1024**2 * 10
        size_down = 0
        while True:
            progress.update_val(size_down)
            buf = fzip.read(buff_size)
            if not buf:
                break
            fext.write(buf)
            size_down += len(buf)
            
        fzip.close()
        fext.close()
        progress.update_final(size_down, "Installed")
        
    # --- Used internally -----------------------------------------------
    def get_map_extractor(self, archive_path):
        """
        Create file like object, that extracts the map from the zip file.
        Additionally returns some metadata. 
        
        This function knows the internal structure of the archives that 
        contain the maps. 
        
        Called by ``extract_map`` and get_file_list``.
        
        Argument
        --------
        
        archive_path: str
            Path to archive that contains the map.
        
        Returns
        -------
        
        fzip: file like object
            Object that extracts a map from a zip file. Behaves like a file.
            
        size_total: int
            Uncompressed size of the map.
            
        mod_time: date_time.date_time
            Modification time of the map, from the zip archive.
        """
        raise NotImplementedError()
    
    def get_file_list_base(self, filter_pattern):
        """
        Return a list of locally stored maps. Maps are searched in 
        ``self.download_dir``.
        
        Argument
        --------
        
        filter_pattern: str
            pattern with wildcards to filter the filenames in 
            ``self.download_dir``. For example: "*.map".
            
        Returns
        -------
        
        list[MapMeta]
        """
        dir_names = os.listdir(self.download_dir)
        map_names = fnmatch.filter(dir_names, filter_pattern)
        map_names.sort()
        
        map_metas = []
        for name in map_names:
            archive_name = path.join(self.download_dir, name)
            disp_name = self.make_disp_name(name)
            _, size_total, date_time = self.get_map_extractor(archive_name)
            map_meta = MapMeta(disp_name=disp_name, 
                               full_name=archive_name, 
                               size=size_total, 
                               time=date_time, 
                               description="", 
                               map_type=None)
            map_metas.append(map_meta)
        
        return map_metas
    
class OsmandManager(BaseManager):
    """
    Manage locally stored maps for Osmand.
    """    
    def __init__(self, application_dir):
        BaseManager.__init__(self)
#        self.application_dir = application_dir
        self.download_dir = path.join(application_dir, "osmand")
        
        #Create own subdir of download dir if it does not exist.
        if not path.exists(self.download_dir):
            os.mkdir(self.download_dir)

    def make_disp_name(self, file_name_path):
        """
        Create a canonical name from a file name or path of a locally stored
        zipped map. 
        The canonical name is used in the user interface.
        
        The canonical name has the form:
            "osmand/Country_Name.obf" or
            "osmand/Language.voice"
        """
        _, file_name = path.split(file_name_path)
        disp_name = "osmand/" + file_name.rsplit(".", 1)[0]
        return disp_name
    
    def make_full_name(self, disp_name):
        """
        Create a path to a locally stored map from its canonical name. 
        """
        _, fname = path.split(disp_name)
        full_name = path.join(self.download_dir, fname + ".zip")
        return full_name
    
    def get_file_list(self):
        """
        Return a list of locally stored maps. Maps are searched in 
        ``self.download_dir``.
        
        Return
        -------
        
        list[MapMeta]
        """
        return self.get_file_list_base("*.obf.zip")
        
    def get_map_extractor(self, archive_path):
        """
        Create file like object, that extracts the map from the zip file.
        Additionally returns some metadata. 
        
        This function knows the internal structure of the archives that 
        contain the maps. 
        
        Argument
        --------
        
        archive_path: str
            Path to archive that contains the map.
        
        Returns
        -------
        
        fzip: file like object
            Object that extracts a map from a zip file. Behaves like a file.
            
        size_total: int
            Uncompressed size of the map.
            
        mod_time: date_time.date_time
            Modification time of the map, from the zip archive.
        """
        zip_container = zipfile.ZipFile(archive_path, "r")
#        zip_fnames = zip_container.namelist()
#        print zip_fnames
        zip_finfos = zip_container.infolist()
        zip_fname = zip_finfos[0].filename
        size_total = zip_finfos[0].file_size
        mod_time = datetime.datetime(*zip_finfos[0].date_time)
        fzip = zip_container.open(zip_fname, "r")
        
        return fzip, size_total, mod_time


class OpenandromapsManager(BaseManager):
    """
    Manage locally stored maps for Openandromap.
    """    
    def __init__(self, application_dir):
        BaseManager.__init__(self)
#        self.application_dir = application_dir
        self.download_dir = path.join(application_dir, "oam")
        
        #Create own subdir of download dir if it does not exist.
        if not path.exists(self.download_dir):
            os.mkdir(self.download_dir)
        
    def make_disp_name(self, file_name_path):
        """
        Create a canonical name (display name) from a path of a locally 
        stored zipped map. 
        
        The canonical name is used in the user interface.
        """
        _, file_name = path.split(file_name_path)
        disp_name = "oam/" + file_name.rsplit(".", 1)[0]
        return disp_name
    
    def make_full_name(self, disp_name):
        """
        Create a path to a locally stored map from its canonical name 
        (display name). 
        
        The canonical name has the form:
            "oam/europe_France_North"
            "oam/asia_Kazakhstan"
            
        The full name has the form:
            "app-download-dir/oam/europe_France_North.zip"
            "app-download-dir/oam/asia_Kazakhstan.zip"
        """
        _, fname = disp_name.split("/")
        full_name = path.join(self.download_dir, fname + ".zip")
        return full_name
        
    def get_file_list(self):
        """
        Return a list of locally stored maps. Maps are searched in 
        ``self.download_dir``.
        
        Return
        -------
        
        list[MapMeta]
        """
        return self.get_file_list_base("*.zip")
        
    def get_map_extractor(self, archive_path):
        """
        Create file like object, that extracts the map from the zip file.
        Additionally returns some metadata. 
        
        This function knows the internal structure of the archives that 
        contain the maps. 
        
        Argument
        --------
        
        archive_path: str
            Path to archive that contains the map.
        
        Returns
        -------
        
        fzip: file like object
            Object that extracts a map from a zip file. Behaves like a file.
            
        size_total: int
            Uncompressed size of the map.
            
        mod_time: date_time.date_time
            Modification time of the map, from the zip archive.
        """
        zip_container = zipfile.ZipFile(archive_path, "r")
#        zip_fnames = zip_container.namelist()
#        print zip_fnames
        zip_finfos = zip_container.infolist()
        
        for map_info in zip_finfos:
            if map_info.filename.endswith(".map"):
                break
        else:
            raise ValueError("No *.map file found in archive.")
        
        zip_fname = map_info.filename                      #IGNORE:W0631
        size_total = map_info.file_size                    #IGNORE:W0631
        mod_time = datetime.datetime(*map_info.date_time)  #IGNORE:W0631
        fzip = zip_container.open(zip_fname, "r")
        
        return fzip, size_total, mod_time
        

        
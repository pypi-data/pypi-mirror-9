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
Download maps from server on the internet.
"""

from __future__ import division
from __future__ import absolute_import              

import time
import urllib2
from os import path
import cPickle
import lxml.html
import dateutil.parser
import urlparse

from mob_map_dl.common import MapMeta, TextProgressBar, PartFile


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


class BaseDownloader(object):
    """
    Base class for objects that download maps from the Internet.
    """ 
    list_url = "Put URL of map list here."
    
    def __init__(self, application_dir=None, cache_time=3600):
        """
        Object is initialized with the application's directory by top level.
        """
        self.application_dir = application_dir
        #Directory of the application. Used to cache list of available maps.
        self.cache_time = cache_time
        #Duration in seconds how long a directory listing is cached.
    
    def make_disp_name(self, server_name):
        """
        Create a canonical name from the name, that the server supplies.
        This canonical name is used in the user interface.
        
        The canonical name has the form:
            "project/Country_Name.obf" 
            
        Argument
        --------
        
        full_name: str
            The complete name that is used to address the file. For example
            the download URL. 
            
        Returns
        -------
        
        str
            The canonical name.
        """
        raise NotImplementedError()   
    
    def get_file_list(self):
        """
        Get list of maps for Osmand that are available for download.
        
        Return
        -------
        
        list[MapMeta]
        """
        raise NotImplementedError()   

    
    def download_file(self, srv_url, loc_name, disp_name):
        """
        Download a file from the server and store it in the local file system.
        
        Creates a progress animation in the console window, as maps are 
        usually large files.
        
        Arguments
        ---------
        
        srv_url: str
            URL of the file on the remote server.
            
        loc_name: str
            Name of the file in the local file system.
            
        disp_name: str 
            File name for display in the progress bar.
            
        TODO: Dynamically adapt ``buff_size`` so that the animation is updated
              once per second.  
        """
        fsrv = urllib2.urlopen(srv_url)
        floc = PartFile(loc_name, "wb")
        
        meta = fsrv.info()
        size_total = int(meta.getheaders("Content-Length")[0])
        size_mib = round(size_total / 1024**2, 1)
        msg = "{name} : {size} MiB".format(name=disp_name[0:50], size=size_mib)
        progress = TextProgressBar(msg, val_max=size_total)
        
        buff_size = 1024 * 100
        size_down = 0
        while True:
            progress.update_val(size_down)
            buf = fsrv.read(buff_size)
            if not buf:
                break
            floc.write(buf)
            size_down += len(buf)
            
        fsrv.close()
        floc.close()
        progress.update_final(size_down, "Downloaded")
        
    def get_cached_file_list(self):
        """
        Return the cached list of available maps (and other files).
        Returns ``None`` if cached list is too old, or none exists.
        
        This is a utility function that should only be called inside the 
        download module. High level code should call ``get_file_list``.
        
        Returns
        -------
        
        list[MapMeta] | NoneType
        """
        if not self.application_dir:
            return None
        try:
            pickle_name = str(type(self)) + "-dirlist.pickle"
            pickle_path = path.join(self.application_dir, pickle_name)
            pickle_time = path.getmtime(pickle_path)
            if time.time() - pickle_time > self.cache_time:
                return None
            pickle_file = open(pickle_path, "rb")
            file_list = cPickle.load(pickle_file)
            pickle_file.close()
            return file_list
        except (OSError, cPickle.PickleError):
            return None
    
    def set_cached_file_list(self, file_list):
        """
        Store the list of available maps (and other files) for later reuse.
        Does nothing if application directory is not writable.
        
        Argument
        --------
        
        file_list: list[MapMeta]
        """
        if not self.application_dir:
            return
        try:
            pickle_name = str(type(self)) + "-dirlist.pickle"
            pickle_path = path.join(self.application_dir, pickle_name)
            pickle_file = open(pickle_path, "wb")
            cPickle.dump(file_list, pickle_file, protocol=-1)
            pickle_file.close()
        except (OSError, cPickle.PickleError):
            pass


class OsmandDownloader(BaseDownloader):
    """
    Download maps from the servers of the Osmand project.
    """
    list_url = "http://download.osmand.net/list.php"
    
    def __init__(self, application_dir=None, cache_time=3600):
        BaseDownloader.__init__(self, application_dir, cache_time)
    
    def make_disp_name(self, server_name):
        """
        Create a canonical name from the name, that the server supplies.
        This canonical name is used in the user interface.
        
        The canonical name has the form:
            "osmand/Country_Name.obf" or
            "osmand/Language.voice"
            
        TODO: Method should really take the download URL as input.
              ``make_disp_name`` of local and install components function in 
              a similar way: They take a path as input. 
        """
        #The server delivers name of the form "Country_Name.obf.zip"
        disp_name = "osmand/" + server_name.rsplit(".", 1)[0]
        return disp_name
    
    def get_file_list(self):
        """
        Get list of maps for Osmand that are available for download.
        
        Return
        -------
        
        list[MapMeta]
        
        Note
        ------
        
        The function parses the regular, human readable, HTML document, that
        lists the existing maps for Osmand. It has the following structure:
        
        <html>
            <head> ... </head>
            <body>
                <h1> ... </h1>
                <table>
                    <tr> ... Table headers ... </tr>
                    <tr> ... Nonsense (".gitignore") ... </tr>
                    <tr>
                        <td>
                            <A HREF="/download.php?standard=yes&file=Afghanistan_asia_2.obf.zip">Afghanistan_asia_2.obf.zip</A>
                        </td>
                        <td>03.08.2014</td>
                        <td>8.2</td>
                        <td>
                            Map, Roads, POI, Transport, Address data for 
                            Afghanistan asia
                        </td>
                    </tr>
                    <tr> ... The next map record ... </tr>
                </table>
            </body>
        </html>
        """
        #Return cached file list if it exists and is recent
        cached_file_list = self.get_cached_file_list()
        if cached_file_list:
            return cached_file_list
        
        #Download HTML document with list of maps from server of Osmand project
        u = urllib2.urlopen(self.list_url)
        list_html = u.read()
#        print list_html

        #Parse HTML list of maps
        root = lxml.html.document_fromstring(list_html)
        table = root.find(".//table")
        map_metas = []
        for row in table[2:]:
            link = row[0][0]
            download_url = urlparse.urljoin(self.list_url, link.get("href"))
            map_meta = MapMeta(disp_name=self.make_disp_name(link.text), 
                               full_name=download_url, 
                               size=float(row[2].text) * 1024**2, #[Byte]
                               time=dateutil.parser.parse(row[1].text,
                                                          dayfirst=True), 
                               description=row[3].text, 
                               map_type="osmand")
            map_metas.append(map_meta)
        
        self.set_cached_file_list(map_metas)
        return map_metas
    
    
class OpenandromapsDownloader(BaseDownloader):
    """
    Downloader for maps from the Open Andro Maps project. 
    """
    list_url = "http://www.openandromaps.org/downloads"
    list_urls = ["http://www.openandromaps.org/downloads/europa", 
                 "http://www.openandromaps.org/downloads/deutschland", 
                 "http://www.openandromaps.org/downloads/russlan", 
                 "http://www.openandromaps.org/downloads/usa",
                 "http://www.openandromaps.org/downloads/kanada", 
                 "http://www.openandromaps.org/downloads/sued-und-mittelamerika", 
                 "http://www.openandromaps.org/downloads/australien-neuseeland-ozeanien", 
                 "http://www.openandromaps.org/downloads/asien-naher-osten",
                 "http://www.openandromaps.org/downloads/afrika", 
#                 "http://www.openandromaps.org/downloads/ubersichts-karten"
                 ]

    def __init__(self, application_dir=None, cache_time=3600):
        BaseDownloader.__init__(self, application_dir, cache_time)
    
    def make_disp_name(self, server_name):
        """
        Create a canonical name from the name, that the server supplies.
        This canonical name is used in the user interface.
        
        The some server URLs are:
            "http://www.openandromaps.org/maps/Germany/Germany_Mid_hike.zip"
            "http://www.openandromaps.org/maps/europe/France_North.zip"
            
        The corresponding canonical names are:
            "oam/Germany_Germany_Mid_hike" 
            "oam/europe_France_North"
            
        Argument
        --------
        
        full_name: str
            The complete name that is used to address the file.
            
        Returns
        -------
        
        str
            The canonical name.
        """
        nozip = server_name.rsplit(".",1)[0]
        tail2_lst = nozip.split("/")[-2:]
        disp_name = "oam/" + "_".join(tail2_lst)
        return disp_name
    
    def get_file_list(self):
        """
        Get list of maps for Osmand that are available for download.
        
        Return
        -------
        
        list[MapMeta]
        
        Note
        ------
        
        The function parses the regular, human readable, HTML documents, that
        lists the existing maps for Openandromaps. 
        """
        #Return cached file list if it exists and is recent
        cached_file_list = self.get_cached_file_list()
        if cached_file_list:
            return cached_file_list
        
        map_metas = []
        for url in self.list_urls:
            #Download HTML document with list of maps from server of Osmand project
            downloader = urllib2.urlopen(url)
            list_html = downloader.read()
            
            #Parse HTML list of maps
            root = lxml.html.document_fromstring(list_html)
            table = root.find(".//tbody")
    #        print lxml.html.tostring(table, pretty_print=True)
            for row in table:
                link = row[3][0]
                download_url = link.get("href")
                map_meta = MapMeta(disp_name=self.make_disp_name(download_url), 
                                   full_name=download_url, 
                                   size=float(row[2].text) * 1024**2, #[Byte]
                                   time=dateutil.parser.parse(row[1].text), 
                                   description="", 
                                   map_type="openandromaps")
                map_metas.append(map_meta)
        
        self.set_cached_file_list(map_metas)
        return map_metas

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
The top level functionality of the map down loader.
"""

from __future__ import division
from __future__ import absolute_import              

import time
import argparse
import sys
import fnmatch
import os.path as path
import os
import platform
import subprocess

from mob_map_dl.common import items_sorted, VERSION
from mob_map_dl.download import OsmandDownloader, OpenandromapsDownloader
from mob_map_dl.local import OsmandManager, OpenandromapsManager
from mob_map_dl.install import OsmandInstaller, OruxmapsInstaller


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime


class AppHighLevel(object):
    """
    High level operations of the program, that are not directly relates to the 
    user interface.  
    """
    app_directory_choices = ["~/Downloads/mobile-map-downloader", 
                             "~/mobile-map-downloader"]
    def __init__(self):
        self.app_directory = None
        self.mobile_device = None
        #Low level components
        self.downloaders = {}
        self.local_managers = {}
        self.installers = {}

    #--- Initialization
    def create_low_level_components(self, app_directory = None, 
                                    mobile_device = None):
        """
        Create low level components that do the real work. 
        Must be called before the application can do anything useful.
        
        Some components need additional resources:
        
        * ``self.local_managers`` need a writable directory to store downloaded
          files. Its path is in ``self.app_directory``. This function searches
          for this directory, and create it when none is found.
          
        * ``self.installers`` need a path to a mobile device in 
          ``self.mobile_device``. 
        """
        #Init with predefined values for more easy testing.
        if app_directory:
            self.app_directory = app_directory
        if mobile_device:
            self.mobile_device = mobile_device
            
        if not self.app_directory:
            self.app_directory = self.find_app_directory()
        if not self.app_directory:
            self.app_directory = self.create_app_directory()
        
        if not self.mobile_device:
            dev_list = self.find_mobile_devices()
            if len(dev_list) == 1:
                self.mobile_device = dev_list[0]
            elif len(dev_list) > 1:
                print "Found multiple mobile devices. Please specify a device."
                for device in dev_list:
                    print device
            
        #Create downloaders, they can function without ``app_directory``
        self.downloaders = {"osmand": OsmandDownloader(self.app_directory),
                            "oam": OpenandromapsDownloader(self.app_directory)}
        #Create local managers, they need a directory to store the maps
        if self.app_directory:
            self.local_managers = {
                               "osmand": OsmandManager(self.app_directory),
                               "oam": OpenandromapsManager(self.app_directory)}
        else:
            print "No writable download directory! No downloads are possible."
            
        if self.mobile_device:
            try:
                self.installers = {
                                "osmand": OsmandInstaller(self.mobile_device),
                                "oam": OruxmapsInstaller(self.mobile_device)}
            except OSError, err:
                print "Error while connecting to mobile device:"
                print err
                self.installers = {}
        else:
            print "No mobile device!"
            
    def find_app_directory(self):
        """
        Find the directory of the program.
        
        Do this portably with:
            https://pypi.python.org/pypi/appdirs/1.2.0
        """
        if self.app_directory:
            return self.app_directory
        for app_dir in self.app_directory_choices:
            app_dir = path.expanduser(app_dir)
            if path.isdir(app_dir):
                return app_dir
        return None
        
    def create_app_directory(self):
        """Create a directory for the program."""
        for app_dir in self.app_directory_choices:
            app_dir = path.expanduser(app_dir)
            root, _ = path.split(app_dir)
            if path.isdir(root):
                os.mkdir(app_dir)
                return app_dir
        return None
        
    def find_mobile_devices(self):
        """
        Find mobile devices that are connected to the computer.
        The device in ``self.mobile_device`` is included if present.
        
        Returns
        -------
        
        list[str]
            Directories that represent a mobile device. 
        
        Note
        -----
        
        Taken from:
        http://stackoverflow.com/questions/12672981/python-os-independent-list-of-available-storage-mobile_dirs
                 
        Alternative Dbus solution:
        http://stackoverflow.com/questions/24913655/how-to-get-mounted-on-in-python-for-external-mobile_dirs
        """
        mobile_dirs = []  #The mobile devices that we find
        if self.mobile_device:
            mobile_dirs.append(self.mobile_device)
            
        if platform.system() == "Linux":
            #Parse the output of the "mount" program.
            mount_run = subprocess.Popen('mount', shell=True, 
                                         stdout=subprocess.PIPE)
            mount_out, _err = mount_run.communicate()
            
            all_fsspecs = set()    #some block devices are mounted several times    
            for line in mount_out.split("\n"): #IGNORE:E1103
                try:
                    fsspec, _, fsdir, _, fstype, _opts = line.split(" ")
#                    print fsspec, fsdir, fstype
                except ValueError:
                    continue
                if not fsspec.startswith("/") or fsspec in all_fsspecs:
                    #ignore special devices and duplicates 
                    continue
                if not path.isdir(path.join(fsdir, "Android")):
                    #Identify Android by a special directory 
                    continue
                all_fsspecs.add(fsspec)
                mobile_dirs.append(fsdir)
                 
        elif platform.system() == "Windows":
#            drivelist = subprocess.Popen('wmic logicaldisk get name,description', shell=True, stdout=subprocess.PIPE)
#            drivelisto, err = drivelist.communicate()
#            driveLines = drivelisto.split('\n')
            pass
        elif platform.system() == "MacOSX":
            pass
        
        return mobile_dirs
        
    #--- Information Retrieval 
    def get_filtered_map_list(self, lister_dict, patterns):
        """
        Create a list of maps, that match certain patterns. Matching is
        not case sensitive.
        
        Usage::
            
            app = AppHighLevel()
            app.create_low_level_components()
            maps = app.get_filtered_map_list(app.downloaders, ["*France*"])
            pprint(maps)
        
        Arguments
        ----------
        
        lister_dict: dict[str:object]
            Objects must have a method ``get_file_list() -> [MapMeta]``.
        
        patterns: list[str]
            List of shell wildcard patterns.
            
        Retuns
        --------
        
        list[MapMeta]
        """
        #Get listing of all maps of all servers.
        all_maps = []
        for _, downloader in items_sorted(lister_dict):
            maps = downloader.get_file_list()
            all_maps += maps
        all_maps.sort(key=lambda m: m.disp_name.lower())
        #Filter the names for the patterns. 
        all_matches = []
        for pattern in patterns:
            pattern_low = pattern.lower()
            for map_ in all_maps:
                name_low = map_.disp_name.lower()
                if fnmatch.fnmatchcase(name_low, pattern_low):
                    all_matches.append(map_)
        return all_matches

    #--- File manipulation
    def get_component(self, file_meta, component_dict):
        """
        Get the software component that can handle a certain file.
        
        file_meta: MapMeta
            Record of information about a certain file
            
        component_dict: dict[str:object]
            Dictionary of low level components that do the real work.
            
        Returns
        -------
        
        object
            Low level handler object. Can download files or extract maps from 
            archive.
        """
        disp_name = file_meta.disp_name
        comp_name, _ = path.split(disp_name)
        component = component_dict[comp_name]
        return component
    
    def download_file(self, file_meta):
        """Download a file from the Internet to the local file system."""
        down_comp = self.get_component(file_meta, self.downloaders)
        loca_comp = self.get_component(file_meta, self.local_managers)
        loca_path = loca_comp.make_full_name(file_meta.disp_name)
        down_comp.download_file(srv_url=file_meta.full_name, 
                                loc_name=loca_path, 
                                disp_name=file_meta.disp_name)

    def install_file(self, file_meta):
        """Install a file from the local file system on the mobile device."""
        loca_comp = self.get_component(file_meta, self.local_managers)
        inst_comp = self.get_component(file_meta, self.installers)
        inst_path = inst_comp.make_full_name(file_meta.disp_name)
        loca_comp.extract_map(arch_path=file_meta.full_name, 
                                   map_path=inst_path, 
                                   disp_name=file_meta.disp_name)
        
    def delete_file_mobile(self, file_meta):    
        """Delete file on the mobile device."""
        inst_component = self.get_component(file_meta, self.installers)
        inst_path = inst_component.make_full_name(file_meta.disp_name)
        os.remove(inst_path)
        
    def delete_file_local(self, file_meta):
        """Delete file on the local file system."""
        loca_component = self.get_component(file_meta, self.local_managers)
        loca_path = loca_component.make_full_name(file_meta.disp_name)
        os.remove(loca_path)
        
    #--- High level file operations
    def plan_work(self, source_files, dest_files, mode):
        """
        Plan work, that transforms `source_files` into `dest_files`. For 
        example downloading or installing files.
        
        Arguments
        ---------
        
        source_files, dest_files: list[MapMeta]
            Lists of `MapMeta` records, that represent source files, and 
            already existing destination files.
        
        mode: str
            Control the conditions to perform the work on individual files.
            Legal values are:
            
            "only_missing"
                Do the work only if the destination file does not exist.
                
            "replace_newer"
                Do the work when the source file is newer than the destination
                file. Also do the work, if the destination file does not exist.
                
            "replace_all"
                Do the work for each source file. Possibly existing destination
                files are always overwritten.
                
        Returns
        -------
        
        list[MapMeta]
            Records from ``source_files``. The work should be done with them.
        """
        supported_modes = ["only_missing", "replace_newer", "replace_all"]
        if mode not in supported_modes:
            raise ValueError("Unsupported mode: {}".format(mode))
        
        if mode == "replace_all":
            return source_files[:]
        
        dest_dict = {file_.disp_name: file_ for file_ in dest_files}
        work_files = []
        for source_file in source_files:
            #If there **is no** local map with this name, download it.
            if source_file.disp_name not in dest_dict:
                work_files.append(source_file)
            elif mode == "replace_newer":
                #If there is a local map with this name, 
                #download it if map on server **is newer**.
                dest_file = dest_dict[source_file.disp_name]
                if source_file.time.date() > dest_file.time.date():
                    work_files.append(source_file)
        
        return work_files
    
    def filter_possible_work(self, work_files, component_dict):
        """Remove files that can't be handled by any component."""
        good_work = []
        for file_ in work_files:
            try:
                #Try to get a component that can handle the file, 
                #when we find one the work is considered possible.
                _ = self.get_component(file_, component_dict)
            except KeyError:
                continue
            good_work.append(file_)
        return good_work
        
    def download_install(self, patterns, mode):
        """
        Download and install maps that match certain patterns. 
        
        Arguments
        ---------
        
        patterns: list[str]
            List of patterns with wildcards, that specify maps. 
            For example ["*France*", "*Germany*"]
        
        mode: str
            Control the conditions to download or install a file.
            For details see: `AppHighLevel.plan_work`
        """
        #Download maps
        srv_maps = self.get_filtered_map_list(self.downloaders, patterns)
        loc_maps = self.get_filtered_map_list(self.local_managers, patterns)
        work_maps = self.plan_work(srv_maps, loc_maps, mode)
        down_maps = self.filter_possible_work(work_maps, self.local_managers)
        down_size = 0
        for map_ in down_maps:
            down_size += map_.size
        print "Downloading: {n} files, {s:5.3f} GiB".format(n=len(down_maps), 
                                                       s=down_size / 1024**3)
        for map_ in down_maps:
            self.download_file(map_)
        
        #Install maps
        loc_maps = self.get_filtered_map_list(self.local_managers, patterns)
        dev_maps = self.get_filtered_map_list(self.installers, patterns)
        work_maps = self.plan_work(loc_maps, dev_maps, mode)
        inst_maps = self.filter_possible_work(work_maps, self.installers)
        inst_size = 0
        for map_ in inst_maps:
            inst_size += map_.size
        print "Installing: {n} files, {s:5.3f} GiB".format(n=len(inst_maps), 
                                                      s=inst_size / 1024**3)
        for map_ in inst_maps:
            self.install_file(map_)
        
    def uninstall(self, patterns, delete_local):
        """
        Delete maps on a mobile device, and optionally locally.
        
        Arguments
        ---------
        
        patterns: list[str]
            List of patterns with wildcards, that specify maps. 
            For example ["*France*", "*Germany*"]
        
        delete_local: bool
            If ``True``: 
                Delete files on the local file system and on the mobile device.
            If ``False``:
                Delete files only on the mobile device.
        """
        del_maps = self.get_filtered_map_list(self.installers, patterns)
        del_size = 0
        for map_ in del_maps:
            del_size += map_.size
        print "Deleting: {n} files, {s:5.3f} GiB on mobile device".format(
                                    n=len(del_maps), s=del_size / 1024**3)
        for map_ in del_maps:
            self.delete_file_mobile(map_)
        
        if delete_local:
            del_maps = self.get_filtered_map_list(self.local_managers, patterns)
            del_size = 0
            for map_ in del_maps:
                del_size += map_.size
            print "Deleting: {n} files, {s:5.3f} GiB on local disk".format(
                                        n=len(del_maps), s=del_size / 1024**3)
            for map_ in del_maps:
                self.delete_file_local(map_)
    

class ConsoleAppMain(object):
    """Us being good Java citizens. :-)"""
    def __init__(self):
        self.app = AppHighLevel()
         
    def print_summary_list(self, lister_dict, long_form):
        """
        Print a summary list of maps.
        
        * lister_dict: dict[str:object]
        * long_form: bool
        """
        for name, lister in items_sorted(lister_dict):
            maps = lister.get_file_list()
            size_total = 0
            for map_ in maps:
                size_total += map_.size
            print "{name:<20} {n:>4} files, {size:3.1f} GiB".format(
                        name=name, n=len(maps), size=size_total / 1024**3)
            if long_form:
                if hasattr(lister, "list_url"):
                    print "    URL: {url}".format(url=lister.list_url)
                elif hasattr(lister, "download_dir"):
                    print "    path: {path}".format(path=lister.download_dir)
                elif hasattr(lister, "install_dir"):
                    print "    path: {path}".format(path=lister.install_dir)

    def print_regular_list(self, lister_dict, patterns):
        """
        Print regular list of maps.
        
        * lister_dict: dict[str:object]
        * patterns: list[str]
         """
        maps = self.app.get_filtered_map_list(lister_dict, patterns)
        size_total = 0
        print "{name:<61} {size:<5}  {time:<10}".format(
                                        name="Name", size="[Gib]", time="Time")
        for map_ in maps:
            print "{name:<61} {size:5.3f}  {time:10}".format(
                                        name=map_.disp_name, 
                                        size=map_.size / 1024**3,
                                        time=str(map_.time.date()))
            size_total += map_.size
        print "-" * 79
        print " " * 49 + "{num:>4} files, {size:6.3f} GiB".format(
                        num=len(maps), size=size_total / 1024**3)

    def list_server_maps(self, patterns, long_form=False):
        """
        List maps that are on servers. Performs ``lss`` subcommand.
        
        * patterns: list[str]
        * long_form: bool
        """
        if not patterns:
            self.print_summary_list(self.app.downloaders, long_form)
        else:
            self.print_regular_list(self.app.downloaders, patterns)
            
    def list_downloaded_maps(self, patterns, long_form=False):
        """
        List maps that are on the local file system. 
        Performs ``lsd`` subcommand.
        """
        if not patterns:
            self.print_summary_list(self.app.local_managers, long_form)
        else:
            self.print_regular_list(self.app.local_managers, patterns)
            
    def list_mobile_maps(self, patterns, long_form=False):
        """
        List maps that are on a mobile device. 
        Performs ``lsm`` subcommand.
        """
        if not patterns:
            self.print_summary_list(self.app.installers, long_form)
        else:
            self.print_regular_list(self.app.installers, patterns)
            
    def download_install(self, patterns, mode):
        """
        Download maps from the Internet and install them on a mobile device.
        
        * patterns: list[str]
        * mode: str
        """
        self.app.download_install(patterns, mode)
        
    def uninstall(self, patterns, delete_local=False):
        """
        Delete maps on a mobile device, and optionally locally.
        """
        self.app.uninstall(patterns, delete_local)
    
    def parse_aguments(self, cmd_args):
        """Parse the command line arguments"""
        parser = argparse.ArgumentParser(description=
                    "Download and install maps for mobile devices.")
        parser.add_argument("-m", "--mobile_device", metavar="DIR",
                            help="directory that represents the mobile device")
        parser.add_argument("--version", action="version", 
                            version="Version: " + VERSION)
#        parser.add_argument("-v", "--verbose", action="store_true",
#                            help="output additional information for "
#                                 "troubleshooting.")
        subparsers = parser.add_subparsers(
            dest="subcommand", title="Subcommands",
            help='all subcommands have an option "-h", for additional help')
        
        lss_parser = subparsers.add_parser(
            "lss", help="list maps on servers on the Internet",
            description="list maps on servers on the Internet")
        lss_parser.add_argument("-l", "--long_form", action="store_true",
                                help="display additional information")
        lss_parser.add_argument("patterns", type=str, nargs="*", metavar="PAT", 
                                help="pattern that selects maps, for example:"
                                     '"osmand/France*", must be quoted')

        lss_parser = subparsers.add_parser(
            "lsd", help="list maps that have been downloaded",
            description="list maps that have been downloaded")
        lss_parser.add_argument("-l", "--long_form", action="store_true",
                                help="display additional information")
        lss_parser.add_argument("patterns", type=str, nargs="*", metavar="PAT", 
                                help="pattern that selects maps, for example:"
                                     '"osmand/France*", must be quoted')

        lss_parser = subparsers.add_parser(
            "lsm", help="list maps on mobile devices",
            description="list maps on mobile devices")
        lss_parser.add_argument("-l", "--long_form", action="store_true",
                                help="display additional information")
        lss_parser.add_argument("patterns", type=str, nargs="*", metavar="PAT", 
                                help="pattern that selects maps, for example:"
                                     '"osmand/France*", must be quoted')
        
        install_prs = subparsers.add_parser(
            "install", help="download maps and install them",
            description="Download maps from the Internet and install them on"
                        "a mobile device. As default only downloads and "
                        "installs missing maps. Use option '-u' to update to "
                        "newer version of a map.")
        install_prs.add_argument("-u", "--update_newer", action="store_true",
                                 help="update maps if newer version is "
                                      "available")
        install_prs.add_argument("-f", "--force_update", action="store_true",
                                 help="update all maps that match the pattern")
#        install_prs.add_argument("-l", "--long_form", action="store_true",
#                                help="display additional information")
        install_prs.add_argument("patterns", type=str, nargs="+", metavar="PAT", 
                                 help="pattern that selects maps, for example:"
                                      '"osmand/France*", must be quoted')
 
        uninst_prs = subparsers.add_parser(
            "uninst", help="remove maps from the mobile device",
            description="remove maps from the mobile device, "
                        "and optionally from the local file system.")
        uninst_prs.add_argument("-d", "--downloaded", action="store_true",
                                help="additionally remove the downloaded "
                                     "maps from the local file system")
        uninst_prs.add_argument("patterns", type=str, nargs="+", metavar="PAT", 
                                 help="pattern that selects maps, for example:"
                                      '"osmand/France*", must be quoted')
       
        args = parser.parse_args(cmd_args)
#        print args
        
        self.app.mobile_device = args.mobile_device
        
        if args.subcommand == "lss":
            func = self.list_server_maps
            arg_dict = {"long_form": args.long_form, # bool
                        "patterns": args.patterns}   # list[str]
        elif args.subcommand == "lsd":
            func = self.list_downloaded_maps
            arg_dict = {"long_form": args.long_form,
                        "patterns": args.patterns}
        elif args.subcommand == "lsm":
            func = self.list_mobile_maps
            arg_dict = {"long_form": args.long_form,
                        "patterns": args.patterns}
        elif args.subcommand == "install":
            func = self.download_install
            mode = "only_missing"
            if args.update_newer:
                mode = "replace_newer"
            if args.force_update:
                mode = "replace_all"
            arg_dict = {"mode":mode,                 # str
                        "patterns": args.patterns}   # list[str]
        elif args.subcommand == "uninst":
            func = self.uninstall
            arg_dict = {"delete_local":args.downloaded, # bool
                        "patterns": args.patterns}      # list[str]
        else:
            raise RuntimeError("Unrecognized subcommand.")
        
        return func, arg_dict
        
    @staticmethod
    def main():
        """
        The program's main method.
        """
        consoleApp = ConsoleAppMain()
        func, arg_dict = consoleApp.parse_aguments(sys.argv[1:])
        consoleApp.app.create_low_level_components()
        func(**arg_dict) #IGNORE:W0142


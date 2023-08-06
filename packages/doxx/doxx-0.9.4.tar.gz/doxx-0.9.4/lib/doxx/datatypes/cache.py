#!/usr/bin/env python
# encoding: utf-8

import os
import time
import platform

from Naked.toolshed.file import FileReader, FileWriter


class DoxxCache(object):
    def __init__(self):
        self.system = platform.system()
        self.package_repo_list_file = "list.txt"        # the list of packages in the package repository
        self.package_repo_json_file = "packages.json"   # the name:description JSON file of packages in the package repository
    
    #################################
    #
    #  Cache Writer Methods
    #
    #################################
    def cache_textfile(self, file_name, file_text):
        cache_dir_path = self._get_platform_specific_cache_dirpath()    # get the platform specific path to the cache directory
        
        # confirm that the local variable was assigned based upon user system type
        if cache_dir_path is not None:
            if not os.path.isdir(cache_dir_path):
                os.mkdir(cache_dir_path)
            cache_file_path = os.path.join(cache_dir_path, file_name)    # create the path to the file in the cache directory
            if self._write_text_file(cache_file_path, file_text):  # write file to cache storage
                return True   # return True if cached file write OK
            else:
                return False  # return False if fails to write
        else:
            return False  # return False if unable to detect user system

    def cache_packagerepo_list(self, file_text):
        if self.cache_textfile(self.package_repo_list_file, file_text):
            return True
        else:
            return False
        
    def cache_packagerepo_json(self, json_string):
        if self.cache_textfile(self.package_repo_json_file, json_string):
            return True
        else:
            return False
    
    #################################
    #
    #  Cache Reader Methods
    #
    #################################
    def get_cached_textfile(self, file_name):
        cache_file_dir = self._get_platform_specific_cache_dirpath()
        cache_file_path = os.path.join(cache_file_dir, file_name)
        return self._read_text_file(cache_file_path)
    
    def get_cached_packagerepo_list(self):
        cache_file_dir = self._get_platform_specific_cache_dirpath()
        cache_file_path = os.path.join(cache_file_dir, self.package_repo_list_file)
        return self._read_text_file(cache_file_path)
    
    def get_cached_packagerepo_json(self):
        cache_file_dir = self._get_platform_specific_cache_dirpath()
        cache_file_path = os.path.join(cache_file_dir, self.package_repo_json_file)
        return self._read_text_file(cache_file_path)        
    
    #################################
    #
    #  Utility Methods
    #
    #################################
    
    #################################
    # PUBLIC
    #################################
    
    def cached_file_exists(self, file_name):
        cache_file_dir = self._get_platform_specific_cache_dirpath()
        cache_file_path = os.path.join(cache_file_dir, file_name)
        if os.path.isfile(cache_file_path):
            return True
        else:
            return False

    def does_cache_file_require_update(self, file_name, diff_seconds_for_update):
        # diff_seconds_for_update is the number of seconds to consider stale data and need for update
        cache_file_dir = self._get_platform_specific_cache_dirpath()
        cache_file_path = os.path.join(cache_file_dir, file_name)
        current_time = time.time()
        if os.path.isfile(cache_file_path):
            if current_time - os.path.getmtime(cache_file_path) > diff_seconds_for_update:
                return True
            else:
                return False
        else:
            return True  # need to update if the file does not exist
    
    #################################
    # PRIVATE
    #################################
    
    def _get_mac_cachedir(self):
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, "Library", "doxx")    
    
    def _get_linux_cachedir(self):
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, '.doxx')
    
    def _get_windows_cachedir(self):
        return os.path.join(os.environ['APPDATA'], 'doxx')
    
    def _write_text_file(self, file_path, file_text):
        try:
            fw = FileWriter(file_path)
            fw.write(file_text)
            return True
        except Exception:
            return False
        
    def _read_text_file(self, file_path):
        try:
            fr = FileReader(file_path)
            return fr.read()  # return the file text
        except Exception:
            return ""  # return empty string if there is an exception during the read
        
    def _get_platform_specific_cache_dirpath(self):
        # detect user system
        if self.system == "Darwin":
            return self._get_mac_cachedir()
        elif self.system == "Linux":
            return self._get_linux_cachedir()
        elif self.system == "Windows":
            return self._get_windows_cachedir()
        else:
            return None
    
    
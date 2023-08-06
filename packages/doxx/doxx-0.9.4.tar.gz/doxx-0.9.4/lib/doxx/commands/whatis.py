#!/usr/bin/env python
# encoding: utf-8

import json
from doxx.datatypes.cache import DoxxCache
from doxx.datatypes.package import OfficialPackage

from Naked.toolshed.network import HTTP
from Naked.toolshed.system import stdout, stderr


def run_whatis(package_name):
    cache = DoxxCache()
    max_cache_seconds = 86400  # 24 hour file cache (same as search module)
    stdout("[*] doxx: Looking up the package description...")
    if cache.cached_file_exists('packages.json'):  # does the cached file already exist
        if cache.does_cache_file_require_update(cache.package_repo_json_file, max_cache_seconds):  # if so, has the cache time elapsed?
            master_descriptions = _pull_official_repository_descriptions()  # pull new file
            cache.cache_packagerepo_json(master_descriptions)               # push it into the file cache
        else:
            master_descriptions = cache.get_cached_packagerepo_json()       # get the cached file if there is no need to pull a new version
    else:
        master_descriptions = _pull_official_repository_descriptions()      # doesn't exist, go get it
        cache.cache_packagerepo_json(master_descriptions)                   # try to cache it
    
    if len(master_descriptions) > 0:  # dictionary from JSON that contains the package descriptions by package name key
        descriptions_dict = json.loads(master_descriptions)
        test_package_name = package_name.lower().strip()
        if test_package_name in descriptions_dict:
            stdout(" ")
            stdout("    Package: " + test_package_name)
            stdout("Description: " + descriptions_dict[test_package_name])
        else:
            stderr("[!] doxx: Unable to locate the package '" + test_package_name + "'", exit=1)
    else:
        stderr("[!] doxx: Unable to read the descriptions file.  It appears to be empty...", exit=1)
        

def _pull_official_repository_descriptions():
    package = OfficialPackage()
    master_package_descriptions = package.get_master_package_description_json_url()
    http = HTTP(master_package_descriptions)
    try:
        if http.get_status_ok():
            master_descriptions = http.res.text
            return master_descriptions.strip()
        else:
            stderr("[!] doxx: Unable to pull remote repository descriptions (HTTP status code: " + str(http.res.status_code) + ")", exit=1)
    except Exception as e:
        stderr("[!] doxx: Unable to pull remote repository descriptions Error: " + str(e) + ")", exit=1)
        
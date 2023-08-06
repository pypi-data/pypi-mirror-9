#!/usr/bin/env python
# encoding: utf-8

from doxx.datatypes.cache import DoxxCache
from doxx.datatypes.package import OfficialPackage
from Naked.toolshed.system import stdout, stderr
from Naked.toolshed.network import HTTP


def run_repoupdate():
    cache = DoxxCache()
    
    # confirm that user is not attempting updates too rapidly (10 sec lockout)
    lockout_time = 10
    # test list.txt file
    if cache.cached_file_exists(cache.package_repo_list_file):
        if not cache.does_cache_file_require_update(cache.package_repo_list_file, lockout_time):
            stderr("[!] doxx: There is a " + str(lockout_time) + " second lockout on repository file updates. Take a break, then try again.", exit=1)
            
    # test packages.json file
    if cache.cached_file_exists(cache.package_repo_json_file):
        if not cache.does_cache_file_require_update(cache.package_repo_json_file, lockout_time):
            stderr("[!] doxx: There is a " + str(lockout_time) + " second lockout on repository file updates. Take a break, then try again.", exit=1)
    
    stdout("[*] doxx: Pulling the list of packages in the Package Repository")
    # pull the master list of the packages included in the Package Repository
    master_list = _pull_official_repository_list()
    if len(master_list) > 0:
        cache.cache_packagerepo_list(master_list)
    else:
        stderr("[!] doxx: Unable to update the " + cache.package_repo_list_file + " file.")
        
    if not cache.cached_file_exists(cache.package_repo_list_file):
        stderr("[!] doxx: Unable to update the " + cache.package_repo_list_file + " file.")
        
    # pull the descriptions of the packages included in the Package Repository
    stdout("[*] doxx: Pulling the descriptions of packages in the Package Repository")
    master_description_json = _pull_official_repository_json()
    if len(master_description_json) > 0:
        cache.cache_packagerepo_json(master_description_json)
    else:
        stderr("[!] doxx: Unable to update the " + cache.package_repo_json_file + " file.", exit=1)
        
    if not cache.cached_file_exists(cache.package_repo_json_file):
        stderr("[!] doxx: Unable to update the " + cache.package_repo_json_file + " file.", exit=1)
    
    stdout("[*] doxx: repoupdate complete")


def _pull_official_repository_list():
    package = OfficialPackage()
    master_package_list_url = package.get_master_package_list_url()
    http = HTTP(master_package_list_url)
    try:
        if http.get_status_ok():
            master_list = http.res.text
            return master_list.strip()   # strip additional spaces, blank end lines off of the list
        else:
            stderr("[!] Unable to pull the remote repository list (HTTP status code: " + str(http.res.status_code) + ")", exit=1)
    except Exception as e:
        stderr("[!] doxx: Unable to pull the remote repository list. Error: " + str(e), exit=1)


def _pull_official_repository_json():
    package = OfficialPackage()
    master_package_json_url = package.get_master_package_description_json_url()
    http = HTTP(master_package_json_url)
    try:
        if http.get_status_ok():
            master_list = http.res.text
            return master_list.strip()   # strip additional spaces, blank end lines off of the list
        else:
            stderr("[!] Unable to pull the remote repository package descriptions (HTTP status code: " + str(http.res.status_code) + ")", exit=1)
    except Exception as e:
        stderr("[!] doxx: Unable to pull the remote repository package descriptions. Error: " + str(e), exit=1)  
#!/usr/bin/env python
# encoding: utf-8

import heapq

from doxx.datatypes.package import OfficialPackage
from doxx.utilities.fuzzysearch import FuzzySearcher
from doxx.datatypes.cache import DoxxCache
from Naked.toolshed.system import stdout, stderr
from Naked.toolshed.network import HTTP


def run_search(search_string):
    # check for local cached list of the repositories, if not present pull the remote repository list from Amazon S3 store
    stdout("[*] doxx: Searching remote doxx repositories...")
    master_text = _get_master_text()
    master_list = _get_master_list(master_text)
    search_word_count = len(search_string.split(" "))
    
    # fuzzy search for user search string
    fuzzy = FuzzySearcher(search_string)
    
    # maxheaps for best results and possible results
    best_results = []
    possible_results = []
    
    # indices for maxheap pushes (allows order of matching priorities by FIFO)
    best_index = 0
    possible_index = 0
    
    # iterate through the repository names
    for repository in master_list:
        best_ratio = 0
        continue_match_attempts = True
        
        # full string match attempt
        match_ratio_fullstring = fuzzy.full_string_ratio(repository)
        if match_ratio_fullstring > best_ratio:
            best_ratio = match_ratio_fullstring
        if match_ratio_fullstring == 1.0:    # perfect match, add to good_results
            continue_match_attempts = False
            heapq.heappush(best_results, (-1.0, best_index, repository))  # give highest priority level (1.0) for this match
            best_index += 1  # bump the index number
            
        # perfect match on first token in the repository name
        if continue_match_attempts is True:
            match_ratio_firsttoken = fuzzy.partial_firstindexitem_dashsplit_ratio(repository)
            if match_ratio_firsttoken > best_ratio:
                best_ratio = match_ratio_firsttoken
            if match_ratio_firsttoken == 1.0:
                continue_match_attempts = False
                heapq.heappush(best_results, (-0.98, best_index, repository))  # give priority of 0.98 for perfect match
                best_index += 1  # bump index number
                
        # slice the repository name by same number of characters if length > length of the search string
        if continue_match_attempts is True:
            match_ratio_startslice = fuzzy.partial_startslice_ratio(repository)
            if match_ratio_startslice > best_ratio:
                best_ratio = match_ratio_startslice
            if match_ratio_startslice == 1.0:
                continue_match_attempts = False
                heapq.heappush(best_results, (-0.99, best_index, repository))
                best_index += 1
                
        # (single word search strings ONLY) attempt match for repository tokens split on '-'
        if continue_match_attempts is True and search_word_count == 1:
            match_ratio_dashtokens = fuzzy.partial_dashsplit_tokens_ratio(repository)
            if match_ratio_dashtokens > best_ratio:
                best_ratio = match_ratio_dashtokens
            if match_ratio_dashtokens == 1.0:
                continue_match_attempts = False
                heapq.heappush(best_results, (-0.95, best_index, repository))
                best_index += 1
                
        # (multi word search strings ONLY) attempt match for sequential groups of repository tokens that are same word count as search string word count
        if continue_match_attempts is True and search_word_count > 1:
            match_ratio_nword = fuzzy.partial_nword_ratio(repository)
            if match_ratio_nword > best_ratio:
                best_ratio = match_ratio_nword
            if match_ratio_nword == 1.0:
                continue_match_attempts = False
                heapq.heappush(best_results, (-0.99, best_index, repository))
                best_index += 1
                
        # (multi word search strings ONLY) set intersection + remainder matching attempt
        if continue_match_attempts is True and search_word_count > 1:
            match_ratio_set = fuzzy.partial_set_ratio(repository)
            if match_ratio_set > best_ratio:
                best_ratio = match_ratio_set
            if match_ratio_set == 1.0:
                continue_match_attempts = False
                heapq.heappush(best_results, (-0.97, best_index, repository))
                best_index += 1
                
        # match attempts are complete, determine the quality of match if not previously determined and push to appropriate maxheap to store it
        if continue_match_attempts is True:
            if best_ratio > 0.8:
                heapq.heappush(best_results, (-best_ratio, best_index, repository))
                best_index += 1
            elif best_ratio > 0.6 and best_ratio <= 0.8:
                heapq.heappush(possible_results, (-best_ratio, possible_index, repository))
                possible_index += 1
                
    # report results of the fuzzy search for the user's search term
    final_best_results = _get_maxheap_results_list(best_results)
    final_possible_results = _get_maxheap_results_list(possible_results)
    
    if len(final_best_results) > 0:
        stdout(" ")
        for result in final_best_results:
            stdout(result)
    elif len(final_possible_results) > 0:
        stdout("[*] doxx: There were no good matches for your search term.")
        stdout("[*] doxx: Do any of these work? :")
        stdout(" ")
        for result in final_possible_results:
            stdout(result)
        pass  # handle with possible results
    else:
        stdout("[*] doxx: No matches found in the Package Repository.")
        stdout("[*] doxx: Get in touch so that we can build it...")   ## TODO: add mechanism for user package submit
        
    
def _get_master_text():
    ## check the cache for a cached version of the file with appropriate cache duration
    cache = DoxxCache()
    max_cache_seconds = 86400  # 24 hour cache of the repository list (same as whatis module)
    if cache.cached_file_exists(cache.package_repo_list_file):
        if cache.does_cache_file_require_update(cache.package_repo_list_file, max_cache_seconds):
            master_list = _pull_official_repository_list()  # pull the master list text from remote
            cache.cache_packagerepo_list(master_list)  # cache it
        else:
            master_list = cache.get_cached_packagerepo_list()  # if cache duration hasn't expired, read the local cached file
    else:
        master_list = _pull_official_repository_list()  # pull the master list text from remote repository if there is no cached file
        cache.cache_packagerepo_list(master_list)  # cache the remote file
    
    # return the master list to the calling function
    return master_list
    

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


def _get_master_list(master_text):
    return master_text.split('\n')


def _get_maxheap_results_list(maxheap_object):
    results_list = []
    for x in range(len(maxheap_object)):
        results_list.append(heapq.heappop(maxheap_object)[-1])  # pop each result off the heap and append to the list
    
    return results_list

#!/usr/bin/env python
# encoding: utf-8

from Naked.toolshed.system import stderr, stdout
from doxx.commands.pull import pull_binary_file
from doxx.commands.unpack import unpack_run
from os import remove

class GithubRepository(object):
    def __init__(self):
        self.user = ""
        self.repo = ""
        self.branch = ""
        self.is_partial_repo = False
        self.keep_paths_map = {}
        self.url_pull_template = "https://github.com/{{user}}/{{repository}}/archive/{{branch}}.tar.gz"
        self.url_pull = ""  # set in set_properties_with_shortcode method
        
    def set_properties_with_shortcode(self, shortcode, local_keep_path):
        # Syntax = user/repo:branch+keep-file_or_dir
        user_repo_branch_block = ""
        user_repo_block = ""
        
        # parse cherry picked file/dir data
        if '+' in shortcode:
            self.is_partial_repo = True
            shortcode_pluschar_split_parts = shortcode.split('+')         # split on the + char
            user_repo_branch_block = shortcode_pluschar_split_parts[0]    # first part is the user/repo:branch block
            remote_repo_keep_path = shortcode_pluschar_split_parts[1]     # second part is the path to cherry pick file or dir in the remote repo
            self.keep_paths_map[remote_repo_keep_path] = local_keep_path  # map ==>  remote_keep_path : local_keep_path
        else:
            user_repo_branch_block = shortcode                            # no cherry pick shortcode, just assign the shortcode to the string block
            
        # parse branch data
        if ':' in user_repo_branch_block:
            user_repo_block_parts = user_repo_branch_block.split(":")
            self.branch = user_repo_block_parts[1]
            user_repo_block = user_repo_block_parts[0]
        else:
            self.branch = "master"
            user_repo_block = user_repo_branch_block
        
        # parse user and repo data
        user_repo_parts = user_repo_block.split('/')
        self.user = user_repo_parts[0]
        self.repo = user_repo_parts[1]
        
        # define the pull URL for this repository
        self.url_pull = self.url_pull_template.replace("{{user}}", self.user)
        self.url_pull = self.url_pull.replace("{{repository}}", self.repo)
        self.url_pull = self.url_pull.replace("{{branch}}", self.branch)
    
    def get_pull_url(self):
        return self.url_pull
    
    def is_partial_repo(self):
        return self.is_partial_repo




class GithubRepoPuller(object):
    def __init__(self):
        pass
    
    def pull_from_key_shortcode_dictionary(self, github_dictionary_from_key):
        # dictionary mapping is "local file or dir path" : "repository file or dir path"
        local_path_list = github_dictionary_from_key.keys()  # create list of local paths from dictionary keys
        
        github_repo_collection = []
        github_fullrepo_collection = []
        github_partialrepo_collection = []
        
        # create the Github repository objects for every path in the key file
        for local_file in local_path_list:
            gh_repo = GithubRepository()
            gh_repo.set_properties_with_shortcode(github_dictionary_from_key[local_file], local_file)
            github_repo_collection.append(gh_repo)

        # iterate through repositories and create collections by repository user/repo/branch
        for repo in github_repo_collection:
            if repo.is_partial_repo == False:
                github_fullrepo_collection.append(repo)
            else:
                if len(github_partialrepo_collection) > 0:
                    match_found = False
                    for test_repo in github_partialrepo_collection:
                        if self.is_same_repo(test_repo, repo):
                            test_repo.keep_paths_map.update(repo.keep_paths_map)  # maintain dictionary with updated paths for a repository
                            match_found = True
                    if match_found is False:
                        github_partialrepo_collection.append(repo)
                else:
                    github_partialrepo_collection.append(repo)
               
        # TESTING     
        # Full Repo Pulls
        if len(github_fullrepo_collection) > 0:
            for repo in github_fullrepo_collection:
                gh_repo_url = repo.get_pull_url()
                targz_filename = repo.repo + "-" + repo.branch + ".tar.gz"  # the name of the pulled archive file
                stdout("[*] doxx: Pulling '" + repo.branch + "' branch of '" + repo.user + "/" + repo.repo + "'")
                
                # pull the github repo as a tar.gz archive
                try:
                    pull_binary_file(gh_repo_url, targz_filename)
                except Exception as e:
                    stderr("[!] doxx: Unable to pull the Github repository.  Error: " + str(e), exit=1)
                    
                # unpack the archive
                if file_exists(targz_filename):
                    root_dir = unpack_run(targz_filename)
                    remove(targz_filename)
                    stdout("[+] doxx: Unpacked to '" + root_dir + "'")
                
        # Cherry picked files and/or directory pulls
        for repo in github_partialrepo_collection:
            print(repo.keep_paths_map)
            print(repo.get_pull_url())
    
    def is_same_repo(self, first_repo, second_repo):
        if first_repo.user == second_repo.user and first_repo.repo == second_repo.repo and first_repo.branch == second_repo.branch:
            return True
        else:
            return False        
#!/usr/bin/env python
# encoding: utf-8

from os import remove
import os.path
from multiprocessing import Process, Lock

from Naked.toolshed.system import stderr, stdout, file_exists
from doxx.commands.pull import pull_binary_file, pull_text_file
from doxx.commands.unpack import unpack_run
from doxx.utilities.filesystem import _create_dirs, _make_os_dependent_path


########################################
#
#  [pull_textfile_runner]
#       public function
#       - pull remote text files
#
########################################


def pull_textfile_runner(text_url_dict):
    """pulls remote text files to local filesystem (public function)"""     
    file_list = list(text_url_dict)       # the local outfile names in a list
    number_of_files = len(file_list)      # the number of files included in the list
    if number_of_files > 0:   
        if number_of_files > 1:  # multiple text file pull, each in separate process
            processes = []       # list of spawned processes
            outputlock = Lock()  # stdout / stderr writes lock
            iolock = Lock()      # input/output lock
            
            # iterate through requested files and execute pull in separate process for each one
            for file_path in file_list:
                p = Process(target=_pull_textfile_multiprocess, args=(file_path, text_url_dict[file_path], outputlock, iolock))
                p.start()
                processes.append(p)
                
            for process in processes:
                process.join(timeout=60)
                
        else:  # single text file pull
            file_path = file_list[0]
            _pull_textfile(file_path, text_url_dict[file_path])  # file_path is local path for write, dictionary value is the URL
    else:
        stderr("[!] doxx: Unable to find text files to pull in the key file", exit=0)


########################################
#
#  [pull_binaryfile_runner]
#       public function
#       - pull remote binary files
#
########################################


def pull_binaryfile_runner(binary_url_dict):
    """pulls remote binary files to local filesystem (public function)"""
    file_list = list(binary_url_dict)     # the local outfile names in a list    
    number_of_files = len(file_list)      # the number of files included in the list
    if number_of_files > 0:   
        if number_of_files > 1:  # multiple binary file pull, each in separate process
            processes = []       # list of spawned processes
            outputlock = Lock()  # stdout / stderr writes lock
            iolock = Lock()      # input/output lock
            
            # iterate through requested files and execute pull in separate process for each one
            for file_path in file_list:
                p = Process(target=_pull_binaryfile_multiprocess, args=(file_path, binary_url_dict[file_path], outputlock, iolock))
                p.start()
                processes.append(p)
                
            for process in processes:
                process.join(timeout=60)
                
        else:  # single text file pull
            file_path = file_list[0]
            _pull_binaryfile(file_path, binary_url_dict[file_path])  # file_path is local path for write, dictionary value is the URL
    else:
        stderr("[!] doxx: Unable to find binary files to pull in the key file", exit=0)


###########################################
#
#  [pull_github_repo_runner]
#       public function
#       - pull remote Github repo archives
#
###########################################


def pull_github_repo_runner(repo_url_dict):
    """pulls remote Github repository archives to the local filesystem and unpacks (public function)"""
    file_list = list(repo_url_dict)       # the local outfile names in a list    
    number_of_files = len(file_list)      # the number of files included in the list
    if number_of_files > 0:   
        if number_of_files > 1:  # multiple binary file pull, each in separate process
            stdout("[*] doxx: Hang in there. Pulling " + str(number_of_files) + " entire repositories. This may take a bit of time...")
            processes = []       # list of spawned processes
            outputlock = Lock()  # stdout / stderr writes lock
            iolock = Lock()      # input/output lock
            
            # iterate through requested files and execute pull in separate process for each one
            for file_path in file_list:
                p = Process(target=_pull_github_repo_multiprocess, args=(file_path, repo_url_dict[file_path], outputlock, iolock))
                p.start()
                processes.append(p)
                
            for process in processes:
                process.join(timeout=120)
                
        else:  # single text file pull
            stdout("[*] doxx: Hang in there. Pulling an entire repository. This may take a bit of time...")
            file_path = file_list[0]
            _pull_github_repo(file_path, repo_url_dict[file_path])  # file_path is local path for write, dictionary value is the URL
    else:
        stderr("[!] doxx: Unable to find binary files to pull in the key file", exit=0)   


###############################################
#
#  [_pull_textfile]
#       private function
#       - execute single process text file pulls
#
###############################################


def _pull_textfile(file_path, url):
    """executes single process text file pulls (private function)"""
    # create OS dependent file path (if necessary)
    file_path = _make_os_dependent_path(file_path)
    # make directory structure if necessary for the file path
    if os.path.dirname(file_path) is not "":
        _create_dirs(file_path)
    # pull the file and write to local filesystem
    try:
        pull_text_file(url, file_path)
    except Exception as e:
        stderr("[!] doxx: Unable to pull '" + file_path + "' from '" + url + "'. Error: " + str(e), exit=1)
        
    if file_exists(file_path):
        stdout("[+] doxx: '" + file_path + "' ...check!")
    else:
        stderr("[!] doxx: There was an error pulling '" + file_path + "'. Error: Unable to locate local file.", exit=1)    
    
    
########################################
#
#  [_pull_textfile_multiprocess]
#       private function
#       - execute multi-file, multiprocess
#           text file pulls
#
########################################


def _pull_textfile_multiprocess(file_path, url, outputlock, iolock):
    """executes multiprocess, multi-file text file pulls (private function)"""
    # create OS dependent file path (if necessary)
    file_path = _make_os_dependent_path(file_path)
    # make directory structure if necessary for the file path
    if os.path.dirname(file_path) is not "":
        iolock.acquire()
        _create_dirs(file_path)
        iolock.release()
    # pull the file and write to local filesystem
    try:
        pull_text_file(url, file_path)
    except Exception as e:
        outputlock.acquire()
        stderr("[!] doxx: Unable to pull '" + file_path + "' from '" + url + "'. Error: " + str(e), exit=0)
        outputlock.release()
    if file_exists(file_path):
        outputlock.acquire()
        stdout("[+] doxx: '" + file_path + "' ...check!")
        outputlock.release()
    else:
        outputlock.acquire()
        stderr("[!] doxx: There was an error pulling '" + file_path + "'. Error: Unable to locate local file", exit=0)
        outputlock.release()


########################################
#
#  [_pull_binaryfile]
#       private function
#       - execute single process binary
#            file pulls
#
########################################


def _pull_binaryfile(file_path, url):
    """executes single process binary file pulls (private function)"""
    # create OS dependent file path (if necessary)
    file_path = _make_os_dependent_path(file_path)
    # make directory structure if necessary for the file path
    if os.path.dirname(file_path) is not "":
        _create_dirs(file_path)
    # pull the file and write to local filesystem    
    try:
        pull_binary_file(url, file_path)
    except Exception as e:
        stderr("[!] doxx: Unable to pull '" + file_path + "' from '" + url + "'. Error: " + str(e), exit=0)
    if file_exists(file_path):
        stdout("[+] doxx: '" + file_path + "' ...check!")
    else:
        stderr("[!] doxx: There was an error pulling '" + file_path + "'. Error: Unable to locate local file.", exit=1) 
    
    
########################################
#
#  [_pull_binaryfile_multiprocess]
#       private function
#       - execute multiprocess multi-file 
#             binary file pulls
#
########################################


def _pull_binaryfile_multiprocess(file_path, url, outputlock, iolock):
    # create OS dependent file path (if necessary)
    file_path = _make_os_dependent_path(file_path)
    # make directory structure if necessary for the file path
    if os.path.dirname(file_path) is not "":
        iolock.acquire()
        _create_dirs(file_path)
        iolock.release()
    # pull the file and write to local filesystem
    try:
        pull_binary_file(url, file_path)
    except Exception as e:
        outputlock.acquire()
        stderr("[!] doxx: Unable to pull '" + file_path + "' from '" + url + "'. Error: " + str(e), exit=0)
        outputlock.release()
    if file_exists(file_path):
        outputlock.acquire()
        stdout("[+] doxx: '" + file_path + "' ...check!")
        outputlock.release()
    else:
        outputlock.acquire()
        stderr("[!] doxx: There was an error pulling '" + file_path + "'. Error: Unable to locate local file", exit=0)
        outputlock.release()


########################################
#
#  [_pull_github_repo]
#       private function
#       - execute single process Github
#             repository archive pulls
#
########################################


def _pull_github_repo(file_path, url):
    """executes single process Github repository archive pulls (private function)"""
    # create OS dependent file path (if necessary)
    file_path = _make_os_dependent_path(file_path)
    # make directory structure if necessary for the file path
    if os.path.dirname(file_path) is not "":
        _create_dirs(file_path)
    # pull the file and write to local filesystem    
    try:
        pull_binary_file(url, file_path)
    except Exception as e:
        stderr("[!] doxx: Unable to pull the archive file from the URL '" + url + "'. Error: " + str(e), exit=0)
    if file_exists(file_path):
        root_dir = unpack_run(file_path)
        remove(file_path)
        stdout("[+] doxx: '" + root_dir + "' ...check!")
    else:
        stderr("[!] doxx: There was an error pulling the repository file. Error: Unable to locate local archive file.", exit=1)


########################################
#
#  [_pull_github_repo_multiprocess]
#       private function
#       - execute multiprocess multi-file 
#             Github repo archive pulls
#
########################################


def _pull_github_repo_multiprocess(file_path, url, outputlock, iolock):
    # create OS dependent file path (if necessary)
    file_path = _make_os_dependent_path(file_path)
    # make directory structure if necessary for the file path
    if os.path.dirname(file_path) is not "":
        iolock.acquire()
        _create_dirs(file_path)
        iolock.release()
    # pull the file and write to local filesystem    
    try:
        pull_binary_file(url, file_path)
    except Exception as e:
        outputlock.acquire()
        stderr("[!] doxx: Unable to pull the archive file from the URL '" + url + "'. Error: " + str(e), exit=0)
        outputlock.release()
    if file_exists(file_path):
        root_dir = unpack_run(file_path)
        remove(file_path)
        outputlock.acquire()
        stdout("[+] doxx: '" + root_dir + "' ...check!")
        outputlock.release()
    else:
        outputlock.acquire()
        stderr("[!] doxx: There was an error pulling the repository file. Error: Unable to locate local archive file.", exit=1)
        outputlock.release()

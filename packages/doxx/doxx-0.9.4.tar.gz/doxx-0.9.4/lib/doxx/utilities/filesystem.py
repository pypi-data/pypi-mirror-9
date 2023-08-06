#!/usr/bin/env python
# encoding: utf-8

import os
from Naked.toolshed.system import dir_exists

########################################
#
# PATHS
#
########################################
def _make_os_dependent_path(file_path):
    """Makes an OS dependent file path from a POSIX or DOS file path"""
    if "/" in file_path:  # POSIX style
        path_list = file_path.split("/")
        os_file_path = os.path.join(*path_list)  # use splat operator to unpack list to tuple of path names
        return os_file_path                      # return the OS dependent path if there are path separators
    elif "\\" in file_path:  # DOS style
        path_list = file_path.split("\\")
        os_file_path = os.path.join(*path_list)  # use splat operator to unpack list to tuple of path names
        return os_file_path         
    else:
        return file_path                         # else simply return file or dir name if there are no path separators
    
    
########################################
#
# DIRECTORIES
#
########################################
def _create_dirs(file_path):
    """Creates a recursive directory path to the requested file name if it does not exist. [file_path] must have correct OS path separators as they are not checked in this function"""
    dir_path = os.path.dirname(file_path)
    if dir_exists(dir_path):
        pass
    else:
        os.makedirs(dir_path)    
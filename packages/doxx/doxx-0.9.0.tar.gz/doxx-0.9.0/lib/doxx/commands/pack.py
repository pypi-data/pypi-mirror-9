#!/usr/bin/env python
# encoding: utf-8

import os
import shutil
import tarfile
import zipfile
from Naked.toolshed.system import stderr


def tar_gzip_package_directory(archive_name, root_dir):
    try:
        current_dir = os.getcwd()  
        archive_gz_name = archive_name + ".tar.gz"
        tar = tarfile.open(archive_gz_name, mode="w:gz", compresslevel=9)    # file writes to current working directory
        os.chdir(root_dir)  # navigate to the root directory to add the files to the archive
        tar.add(".")     # make tar.gz archive
        tar.close()
        os.chdir(current_dir)  # navigate back to user's current working directory
    except Exception as e:
        os.chdir(current_dir)  # if exception was raised, make sure that user is back in their current working directory before raising system exit
        tar.close()
        stderr("[!] doxx: Unable to pack the directory '" + root_dir + "'. Error: " + str(e))
        

def zip_package_directory(archive_name, path):
    try:
        current_dir = os.getcwd()
        archive_name = archive_name + '.zip'
        archive_file_list = []
        os.chdir(path)
        for root, dirs, files in os.walk(os.getcwd()):
            for the_file in files:      
                archive_file_list.append((os.path.relpath(os.path.join(root, the_file))))
        zipper = zipfile.ZipFile(archive_name, 'w')
        for zip_file in archive_file_list:
            zipper.write(zip_file)
        zipper.close()
        shutil.move(archive_name, os.path.join(current_dir, archive_name))
        os.chdir(current_dir)
    except Exception as e:
        os.chdir(current_dir)
        zipper.close()
        stderr("[!] doxx: Unable to pack the directory '" + path + "'. Error: " + str(e))

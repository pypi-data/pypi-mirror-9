#!/usr/bin/env python
# encoding: utf-8

import tarfile
import zipfile
from os import remove
from Naked.toolshed.system import stderr, file_exists


def unpack_run(file_path):
    if tarfile.is_tarfile(file_path):
        return unpack_targz_archive_file(file_path)  # returns the root directory from the unpack function below
    elif zipfile.is_zipfile(file_path):
        return unpack_zip_archive_file(file_path)    # returns the root directory from the unpack function below
    else:
        stderr("[!] doxx: '" + file_path + "' does not appear to be a supported project archive type.  Please review the project archive documentation and try again.", exit=1)


def unpack_targz_archive_file(targz_file_path):
    try:
        tar = tarfile.open(targz_file_path, "r:*")
        # define root directory in the tar archive to return to calling function
        x = 0
        root_dir = None
        for tarinfo in tar:
            if x == 0:
                root_dir = tarinfo.name
                x += 1
            else:
                break
        # unpack the archive
        tar.extractall()
        tar.close()
        # return the root directory to calling function
        return root_dir
    except Exception as e:
        stderr("[!] doxx: Unable to unpack the file '" + targz_file_path + "'. Error: " + str(e))

  
def unpack_zip_archive_file(zip_file_path):
    try:
        zip_archive = zipfile.ZipFile(zip_file_path, 'r')
        # define root directory in the tar archive to return to calling function
        x = 0
        root_dir = None
        for zipinfo in zip_archive.infolist():
            if x == 0:
                root_dir = zipinfo.filename
                x += 1
            else:
                break
        # extract the zip archive
        zip_archive.extractall()
        zip_archive.close()
        
        # if root_dir is actually a file name, then assume root dir is the CWD
        if '.' in root_dir:
            root_dir = "."
        # return the root directory in the zip archive
        return root_dir
    except Exception as e:
        stderr("[!] doxx: Unable to unpack the file '" + zip_file_path + "'. Error: " + str(e))

        
def remove_compressed_archive_file(targz_file_path):
    if file_exists(targz_file_path):
        remove(targz_file_path)
    else:
        pass  # could not find the compressed archive file, raise no error message and abort attempt
    
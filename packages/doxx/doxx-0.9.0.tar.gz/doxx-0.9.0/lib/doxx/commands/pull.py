#!/usr/bin/env python
# encoding: utf-8

import gzip
from os import remove, rename
from Naked.toolshed.network import HTTP
from Naked.toolshed.file import FileWriter
from Naked.toolshed.system import stderr, stdout, file_exists
from Naked.toolshed.python import is_py3
from doxx.commands.unpack import unpack_run


def run_pull(url):
    # URL pulls for project archive packages, gzip files, text files
    if is_url(url):
        file_name = get_file_name(url)
        if len(file_name) == 0:
            file_name = "pullfile"
        
        # begin file pull
        stdout("[*] doxx: Pulling file...")
            
        if is_tar_gz_archive(file_name):
            root_dir = None
            try:
                pull_binary_file(url, file_name)      # pull remote file
            except Exception as e:
                stderr("[!] doxx: Unable to pull the tar.gz project. Error: " + str(e), exit=1)
            stdout("[*] doxx: Unpacking...")
            try:
                root_dir = unpack_archive(file_name)             # unpack archive and define the root directory
            except Exception as e:
                stderr("[!] doxx: Unable to unpack the compressed project file. Error: " + str(e), exit=1)
            if file_exists(file_name):
                remove_file(file_name)                # remove the archive file
            if file_exists('pkey.yaml'):
                if not file_exists('key.yaml'):
                    rename('pkey.yaml', 'key.yaml')   # change name of pkey.yaml to key.yaml if there is not already a key.yaml file
            return root_dir                           # return the root directory path for calling code that needs it
        elif is_zip_archive(file_name):
            root_dir = None
            try:
                pull_binary_file(url, file_name)      # pull remote file
            except Exception as e:
                stderr("[!] doxx: Unable to pull the .zip project. Error: " + str(e), exit=1)
            stdout("[*] doxx: Unpacking...")
            try:
                root_dir = unpack_archive(file_name)             # unpack archive and define the root directory
            except Exception as e:
                stderr("[!] doxx: Unable to unpack the compressed project file. Error: " + str(e), exit=1)
            if file_exists(file_name):
                remove_file(file_name)                # remove the arhcive file
            if file_exists('pkey.yaml'):
                if not file_exists('key.yaml'):
                    rename('pkey.yaml', 'key.yaml')   # change name of pkey.yaml to key.yaml if there is not already a key.yaml file      
            return root_dir                           # return the root directory path for calling code that needs it
        elif is_gzip_file(file_name):
            try:
                pull_binary_file(url, file_name)      # pull the remote gzip file
            except Exception as e:
                stderr("[!] doxx: Unable to pull the compressed file. Error: " + str(e), exit=1)
            stdout("[!] doxx: Decompressing...")
            try:
                decompress_gzip(file_name)           # decompress the file text
            except Exception as e:
                stderr("[!] doxx: Unable to decompress the gzip file. Error: " + str(e), exit=1)
            if file_exists(file_name):
                remove_file(file_name)               # remove the gzip compressed file and leave the decompressed text file
        else:
            try:
                pull_text_file(url, file_name)       # it is assumed to be a plain text template or key file, pull the text
            except Exception as e:
                stderr("[!] doxx: Unable to pull the requested file. Error: " + str(e), exit=1)
    else:
        # SHORT CODES for Github repository, CDNJS, etc
        if "/" in url:
            short_code = url
            short_code_parts = short_code.split('/')
            
            if short_code.startswith('cdnjs:'):
                pass  # add code for cdnjs pulls
            else:
                # default to Github repositories
                if len(short_code_parts) == 2:
                    if "#" in short_code_parts[1]:
                        # contains a request for a specific branch of the Github repository
                        user = short_code_parts[0]
                        if "#" in user:
                            stderr("[!] doxx: the short code for Github repositories is not properly formed")
                            stderr("[!] doxx: the syntax is [user]/[repository]#[branch]", exit=1)
                        repo_parts = short_code_parts[1].split('#')
                        repo = repo_parts[0]
                        branch = repo_parts[1]
                        targz_filename = repo + "-" + branch + ".tar.gz"
                        url = "https://github.com/{{user}}/{{repository}}/archive/{{branch}}.tar.gz"
                        url = url.replace("{{user}}", user)
                        url = url.replace("{{repository}}", repo)
                        url = url.replace("{{branch}}", branch)
                        user_message = "[*] doxx: Pulling branch '" + branch + "' of Github repository '" + user + "/" + repo + "'..."
                    else:
                        # default to the master Github repository branch
                        user = short_code_parts[0]
                        if "#" in user:
                            stderr("[!] doxx: the short code for Github repositories is not properly formed")
                            stderr("[!] doxx: the syntax is [user]/[repository]#[branch]", exit=1)                        
                        repo = short_code_parts[1]
                        targz_filename = repo + "-master.tar.gz"
                        url = "https://github.com/{{user}}/{{repository}}/archive/master.tar.gz"
                        url = url.replace("{{user}}", user)
                        url = url.replace("{{repository}}", repo)
                        user_message = "[*] doxx: Pulling master branch of Github repository '" + user + "/" + repo + "'..."
                     
                    # notify user of the pull   
                    stdout(user_message)
                        
                    try:
                        pull_binary_file(url, targz_filename)  # pull the archive file
                    except Exception as e:
                        stderr("[!] doxx: Unable to pull the Github repository.  Error: " + str(e), exit=1)
                        
                    if file_exists(targz_filename):
                        try:
                            unpack_archive(targz_filename)  # unpack the archive locally
                            remove(targz_filename)          # remove the archive file
                        except Exception as e:
                            stderr("[!] doxx: Unable to unpack the pulled Github repository. Error: " + str(e), exit=1)
                    else:
                        stderr("[!] doxx: The Github repository pull did not complete successfully.  Please try again.")
                else:
                    stderr("[!] doxx: short code syntax for Github repository pulls:", exit=0)
                    stderr("  $ doxx pull [user]/[repository]")
                    stderr("with an optional branch")
                    stderr("  $ [user]/[repository]#[branch]")
            
        # PROJECT PACKAGES - official repository package pulls
        else:  
            from doxx.datatypes.package import OfficialPackage
            package_name = url
            package = OfficialPackage()
            package_url = package.get_package_targz_url(package_name)
            package_archive_name = package_name + ".tar.gz"
            root_dir = None
            # pull the package archive file
            stdout("[*] doxx: Pulling package '" + package_name + "'...")
            try:
                pull_binary_file(package_url, package_archive_name)
            except Exception as e:
                stderr("[!] doxx: Unable to pull the doxx repository package.  Error: " + str(e), exit=1)
            # unpack the archive file
            stdout("[*] doxx: Unpacking...")
            try:
                root_dir = unpack_archive(package_archive_name)             # unpack archive and define the root directory
            except Exception as e:
                stderr("[!] doxx: Unable to unpack the project package. Error: " + str(e), exit=1)            
            # remove the archive file
            if file_exists(package_archive_name):
                remove_file(package_archive_name)                # remove the archive file
            if file_exists('pkey.yaml'):
                if not file_exists('key.yaml'):
                    rename('pkey.yaml', 'key.yaml')              # change name of pkey.yaml to key.yaml if there is not already a key.yaml file            
            return root_dir                                      # return the root directory path for calling code that needs it            


def is_url(url):
    """test for HTTP and HTTPS protocol in the string"""
    if len(url) > 6 and (url[0:7] == "http://" or url[0:8] == "https://"):
        return True
    else:
        return False


def is_tar_gz_archive(file_name):
    """test for tar.gz file archive"""
    if file_name.lower().endswith('.tar.gz') or file_name.lower().endswith('.tar.gzip'):
        return True
    else:
        return False


def is_zip_archive(file_name):
    """test for zip file archive extension"""
    if file_name.lower().endswith('.zip'):
        return True
    else:
        return False


# must be tested AFTER tests for tar.gz archive because both will test true
def is_gzip_file(file_name):
    """test for gzip compressed file extension"""
    if file_name.lower().endswith('.gz') or file_name.lower().endswith('.gzip'):
        return True
    else:
        return False


def get_file_name(url):
    """returns the filename from a URL"""
    split_url = url.split('/')
    return split_url[-1]


def pull_binary_file(url, binary_file_name):
    """pulls a remote binary file and writes to disk"""
    # pull the binary file data
    http = HTTP(url)
    try:
        if http.get_status_ok():
            binary_data = http.res.content    
            # write binary data to disk
            try:
                fw = FileWriter(binary_file_name)
                fw.write_bin(binary_data)
            except Exception as e:
                stderr("[!] doxx: File write failed for '" + binary_file_name + "'.  Error: " + str(e), exit=1)
        else:
            fail_status_code = http.res.status_code
            if fail_status_code == 404:
                stderr("[!] doxx: Unable to pull the file because it does not appear to exist. (HTTP status code: " + str(fail_status_code) + ")", exit=1)
            else:
                stderr("[!] doxx: Unable to pull '" + url + "'. (HTTP status code: " + str(fail_status_code) + ")", exit=1)
    except Exception as e:
        stderr("[!] doxx: Unable to pull '" + url + "'. Error: " + str(e), exit=1)


def pull_text_file(url, text_file_name):
    """pulls a remote text file and writes to disk"""
    # pull the binary file data
    http = HTTP(url)
    try:
        if http.get_status_ok():
            text_data = http.res.text
            # write text data to disk
            try:
                fw = FileWriter(text_file_name)
                fw.write(text_data)
            except Exception as e:
                stderr("[!] doxx: File write failed for '" + text_file_name + "'.  Error: " + str(e), exit=1)
        else:
            fail_status_code = http.res.status_code
            stderr("[!] doxx: Unable to pull '" + url + "' (HTTP status code " + str(fail_status_code) + ")", exit=1)
    except Exception as e:
        stderr("[!] doxx: Unable to pull '" + url + "'. Error: " + str(e), exit=1)


def unpack_archive(archive_file_name):
    """unpacks a tar.gz or zip file archive and writes to local disk"""
    root_dir = unpack_run(archive_file_name)  # root directory of unpacked archive returned from the unpack function, returned from this function if calling code needs it
    return root_dir


def decompress_gzip(gz_filename):
    """decompress gzip compressed file"""
    # decompress the gzip'd file
    f = gzip.open(gz_filename, 'rb')
    file_content = f.read()
    f.close()
    
    # monkeypatch for Python 3 byte string read issue
    if is_py3():
        file_content = str(file_content)
    
    # get the base file name for the decompressed file write
    filename_split = gz_filename.split('.')
    if len(filename_split) == 2:
        basename = filename_split[0]
    elif len(filename_split) > 2:
        basename = filename_split[0] + '.' + filename_split[1]  # concatenate first two parts of file name (e.g. example + '.' + 'tar' )
    else:
        basename = gz_filename
        
    # write the file locally
    fw = FileWriter(basename)
    fw.write(file_content)


def remove_file(file_name):
    """removes archive file that was pulled from a remote source"""
    if file_exists(file_name):
        remove(file_name)
        
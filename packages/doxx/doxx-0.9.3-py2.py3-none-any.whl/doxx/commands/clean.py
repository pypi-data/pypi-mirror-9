#!/usr/bin/env python
# encoding: utf-8

from os import remove
from shutil import rmtree
from Naked.toolshed.system import list_filter_files, list_filter_files_cwd, list_all_files, dir_exists, file_exists, make_path, stderr, stdout


def run_clean():
    _remove_key()
    _remove_doxt()
    stdout("[*] doxx: Clean complete.")


def _remove_key():
    # remove key.yaml
    if file_exists('key.yaml'):
        try:
            remove('key.yaml')
            stdout("[-] doxx: -- key.yaml ... removed")
        except Exception as e:
            stderr("[!] doxx: Unable to remove 'key.yaml'. Error: " + str(e), exit=0)
    
    # remove pkey.yaml (project archives)
    if file_exists('pkey.yaml'):
        try:
            remove('pkey.yaml')
            stdout("[-] doxx: -- pkey.yaml ... removed")
        except Exception as e:
            stderr("[!] doxx: Unable to remove 'pkey.yaml'. Error: " + str(e), exit=0)
    
    # remove project.yaml (project archives)
    if file_exists('project.yaml'):
        try:
            remove('project.yaml')
            stdout("[-] doxx: -- project.yaml ... removed")
        except Exception as e:
            stderr("[!] doxx: Unable to remove 'project.yaml'. Error: " + str(e), exit=0)     

     
def _remove_doxt():
    # check main directory
    cwd_doxt_list = list_filter_files_cwd(".doxt")
    
    # check for a templates directory
    if dir_exists('templates'):
        templates_dir_doxt_list = list_filter_files(".doxt", "templates")
    else:
        templates_dir_doxt_list = []
    
    # remove template files from the working directory
    if len(cwd_doxt_list) > 0:
        for doxt_file in cwd_doxt_list:
            try:
                remove(doxt_file)
                stdout("[-] doxx: -- " + doxt_file + " ... removed")
            except Exception as e:
                stderr("[!] doxx: Unable to remove the file " + doxt_file + "'. Error: " + str(e), exit=0)
    
    # remove any template files from the templates directory
    if len(templates_dir_doxt_list) > 0:
        for doxt_file in templates_dir_doxt_list:
            new_doxt_path = make_path('templates', doxt_file)
            remove(new_doxt_path)
            stdout("[-] doxx: -- " + new_doxt_path + " ... removed")
            
    # if there are files still remaining in the templates directory, leave it
    # otherwise, remove the templates directory as well
    if dir_exists('templates'):
        remaining_template_file_list = list_all_files('templates')  # get the remaining non-.doxt files in the directory
        if len(remaining_template_file_list) > 0:
            pass  # do nothing, skip the removal of the 'templates' directory from the project because other files are present in it
        else:
            try:
                rmtree('templates')
                stdout("[-] doxx: -- templates (directory) ... removed")
            except Exception as e:
                stderr("[!] doxx: Unable to remove the 'templates' directory.  Error: " + str(e), exit=1)
                
                
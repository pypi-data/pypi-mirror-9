#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from multiprocessing import Process, Lock

from Naked.toolshed.file import FileWriter
from Naked.toolshed.system import cwd, dir_exists, file_exists, make_dirs, make_path, stderr, stdout
from Naked.toolshed.python import is_py2

from doxx.datatypes.template import DoxxTemplate, RemoteDoxxTemplate
from doxx.datatypes.key import DoxxKey
from doxx.commands.pull import run_pull, is_url
from doxx.commands.unpack import unpack_run

# need a different template for Python 2 & 3
if is_py2():    
    from doxx.renderer.inkpy2 import Template as InkTemplate
    from doxx.renderer.inkpy2 import Renderer as InkRenderer
else:
    from doxx.renderer.inkpy3 import Template as InkTemplate
    from doxx.renderer.inkpy3 import Renderer as InkRenderer


def multi_process_build(key, key_path):
    processes = []       # list of spawned processes
    iolock = Lock()      # file read / write lock
    outputlock = Lock()  # stdout / stderr writes lock
    
    # ## SINGLE PROCESS
    # for template in key.meta_data['templates']:
        # b = Builder()
        # b.set_key_data(key)
        # b.single_template_run(template)
    
    ## MULTI-PROCESS    
    # create worker processes
    for template in key.meta_data['templates']:
        p = Process(target=single_process_runner, args=(template, key, key_path, iolock, outputlock))
        p.start()
        processes.append(p)
    # join worker processes upon completion or with 60 second timeout
    for process in processes:
        process.join(timeout=60)
    
    # ## zombie process finder for testing
    # active_child_processes = active_children()
    
    # if len(active_child_processes) > 0:
        # print("active children detected")
    # else:
        # print("no active children detected")


def single_process_runner(template_path, key, key_path, iolock, outputlock):
    b = Builder(key_path)
    b.set_key_data(key)
    b.multi_process_run(template_path, iolock, outputlock)


class Builder(object):
    """The Builder class renders doxx templates from user provided keys"""
    def __init__(self, key_path): 
        self.key_path = key_path   # the local key file path: key.yaml or as specified by user
        self.key_data = {}
        self.no_key_replacements = False
    
    def run(self):
        doxxkey = DoxxKey(self.key_path)
        # detect single vs multiple keys in the template and execute replacements with every requested template
        self.set_key_data(doxxkey)  # assign key data from the doxx Key
        
        try:
            # are there Github repository(ies) to pull? if so, do it
            if doxxkey.github_repo_key is True:
                from doxx.datatypes.remotefiles import pull_github_repo_runner
                pull_github_repo_runner(doxxkey.meta_data['github-repos'])
            
            # are there text file(s) to pull? if so, do it
            if doxxkey.textfile_key is True:
                from doxx.datatypes.remotefiles import pull_textfile_runner
                pull_textfile_runner(doxxkey.meta_data['textfiles'])
                
            # are there binary files to pull? if so, do it
            if doxxkey.binaryfile_key is True:
                from doxx.datatypes.remotefiles import pull_binaryfile_runner
                pull_binaryfile_runner(doxxkey.meta_data['binaryfiles'])
                
            # process templates/archive files
            if doxxkey.project_key is True:  # the key is set to run on a local or remote project archive
                self.project_archive_run(doxxkey)
            elif doxxkey.multi_template_key is True:  # the key is set to run on multiple local or remote template files
                multi_process_build(doxxkey, self.key_path)
            elif doxxkey.single_template_key is True:
                self.single_template_run(doxxkey.meta_data['template']) # the key is set to run on a single local or remote template file
            else:
                pass  # no default condition
        except Exception as e:
            stderr("[!] doxx: Error: " + str(e), exit=1)
            
    
    def set_key_data(self, key):
        """used to set the key data"""
        self.key_data = key.key_data
        self.no_key_replacements = key.no_replacements  # defined True if there were no replacement keys in the key file, used to indicate skip replacements in the template(s)
        
    
    def single_template_run(self, template_path):
        """Render replacements using a single template file as defined in a doxx key file (public method)"""
        #----------------------------------------------------------------------------
        # NOTE : changes in this method require the same changes to multi_process_run
        #----------------------------------------------------------------------------       
        ## Load the data
        # remote templates
        if len(template_path) > 6 and (template_path[0:7] == "http://" or template_path[0:8] == "https://"):
            template = RemoteDoxxTemplate(template_path)
            try:
                result = template.load_data()
                if result[0] == False:  # if the method responds False, then HTTP data load did not work
                    stderr(result[1], exit=1)  # write out the returned error message in result[1] position of the tuple
                    # halt execution if unsuccessful
            except Exception as e:
                stderr("[!] doxx: Unable to load the remote template file '" + template_path + "'. Error message: " + str(e), exit=1)
        # local templates        
        elif file_exists(template_path):
            template = DoxxTemplate(template_path)
            try:
                template.load_data()
            except Exception as e:
                stderr("[!] doxx: Unable to read the local template file '" + template_path + "'. Error message: " + str(e), exit=1)
        else:
            stderr("[!] doxx: Unable to find the requested template file " + template_path, exit=1)  # print error message and halt execution of application
         
        ## Split the data  
        try:
            template.split_data()
        except Exception as e:
            stderr("[!] doxx: Unable to parse the template data.  Please verify the template syntax and try again.  Error message: " + str(e), exit=1)
        
        ## Parse data for errors
        error_parse_result = template.parse_template_for_errors()
        
        if error_parse_result[0] == True:          # if there was a parsing error
            stderr(error_parse_result[1], exit=1)  # print the returned error message to stderr and exit application
        
        ## Then parse the template text and load instance attributes for the text replacement with Ink below
        try:
            template.parse_template_text()
        except Exception as e:
            stderr("[!] doxx: An error occurred while parsing the template file. Error message: " + str(e), exit=1)
    
        # determine whether this is a verbatim template file (no replacements) or the key file did not include replacement keys
        if template.verbatim is True or self.no_key_replacements is True:
            # write template.text out verbatim
            try:
            # if the requested destination directory path does not exist, make it
                outfile_dir_path = make_path(os.path.dirname(self.key_path), os.path.dirname(template.outfile))
                if not outfile_dir_path == '' and not dir_exists(outfile_dir_path):
                    make_dirs(outfile_dir_path)
                # write the file
                outfile_path = make_path(os.path.dirname(self.key_path), template.outfile)
                fw = FileWriter(outfile_path)
                fw.write(template.text)
                stdout("[+] doxx: '" + outfile_path + "' build... check")
            except Exception as e:
                stderr("[!] doxx: There was a file write error. Error message: " + str(e), exit=1)        
        else:
            # template meta data is in template.meta_data
            # template text is in template.text
            # perform the text replacements:         
            try:
                ink_template = InkTemplate(template.text)
                ink_renderer = InkRenderer(ink_template, self.key_data)
                rendered_text = ink_renderer.render()
            except Exception as e:
                stderr("[!] doxx: An error occurred during the text replacement attempt.  Error message: " + str(e), exit=1)
        
            # if the requested destination directory path does not exist, make it
            outfile_dir_path = make_path(os.path.dirname(self.key_path), os.path.dirname(template.outfile))
            if not outfile_dir_path == '' and not dir_exists(outfile_dir_path):
                make_dirs(outfile_dir_path)
    
            # write rendered file to disk
            try:
                outfile_path = make_path(os.path.dirname(self.key_path), template.outfile)
                fw = FileWriter(outfile_path)
                fw.write(rendered_text)
                stdout("[+] doxx: -- " + outfile_path + " ... check")
            except Exception as e:
                stderr("[!] doxx: There was an error with the rendered file write. Error message: " + str(e), exit=1)
            
    def multi_process_run(self, template_path, iolock, outputlock):
        """Render replacements over multiple template files as defined in doxx key file using multiple processes (public method)"""
        #-------------------------------------------------------------------------------
        # NOTE : changes in this method require the same changes to single_template_run
        #-------------------------------------------------------------------------------
        ## Load the data
        if len(template_path) > 6 and (template_path[0:7] == "http://" or template_path[0:8] == "https://"):
            template = RemoteDoxxTemplate(template_path)
            try:
                result = template.load_data()  # load remote template file through HTTP or HTTPS protocol
                if result[0] == False:  # if the method responds False, then HTTP data load was not successful
                    outputlock.acquire()
                    stderr(result[1], exit=0)  # write out the returned error message in result[1] position of the tuple
                    outputlock.release()
                    sys.exit(1)  # release the lock before raising SystemExit
            except Exception as e:
                outputlock.acquire()
                stderr("[!] doxx: Unable to load the remote template file '" + template_path + "'. Error message: " + str(e), exit=0)
                outputlock.release()
                sys.exit(1)  # release the lock before raising SystemExit
        elif file_exists(template_path):
            template = DoxxTemplate(template_path)
            
            iolock.acquire()  # acquire the IO lock for template file read
            try:
                template.load_data()  # load local data
            except Exception as e:
                outputlock.acquire()
                stderr("[!] doxx: Unable to read the local template file '" + template_path + "'. Error message: " + str(e), exit=0)
                outputlock.release()
                sys.exit(1)  # release the lock before raising SystemExit
            iolock.release()  # release the IO lock for template file read
        else:
            outputlock.acquire()  # acquire the stderr lock
            stdout("[!] doxx: Unable to find the requested template file " + template_path)  # print error message in standard output, multi-file run so do not end execution of application       
            outputlock.release()  # release the stderr lock

        ## Split the data
        try:
            template.split_data()  # split the data sections
        except Exception as e:
            outputlock.acquire()
            stderr("[!] doxx: Unable to parse the template data.  Please verify the template syntax and try again.  Error message: " + str(e), exit=0)
            outputlock.release()
            sys.exit(1)  # release the lock before raising SystemExit
            
        ## Parse the data for errors
        error_parse_result = template.parse_template_for_errors()
        
        if error_parse_result[0] == True:          # if there was a parsing error
            outputlock.acquire()
            stderr(error_parse_result[1], exit=0)  # print the returned error message to stderr and exit application
            outputlock.release()
            sys.exit(1)  # release the lock before raising SystemExit
    
        ## Parse the template text
        try:
            template.parse_template_text()
        except Exception as e:
            outputlock.acquire()
            stderr("[!] doxx: An error occurred during the attempt to parse the template file. Error message: " + str(e), exit=0)
            outputlock.release()
            sys.exit(1)  # release the lock before raising SystemExit
        
        # determine whether this is a verbatim template file (no replacements) or the key file did not include replacement keys
        if template.verbatim is True or self.no_key_replacements is True:
            # write template.text out verbatim
            try:
                # if the requested destination directory path does not exist, make it
                outfile_dir_path = make_path(os.path.dirname(self.key_path), os.path.dirname(template.outfile))
                try:
                    iolock.acquire()
                    if not outfile_dir_path == '' and not dir_exists(outfile_dir_path):
                        make_dirs(outfile_dir_path)
                    iolock.release()
                except Exception as e:
                    iolock.release()  # release the lock then re-raise the exception
                    raise e
                # write the file
                outfile_path = make_path(os.path.dirname(self.key_path), template.outfile)
                # then write the file out verbatim
                try:
                    iolock.acquire()
                    fw = FileWriter(outfile_path)
                    fw.write(template.text)
                    iolock.release()
                except Exception as e:
                    iolock.release()  # catch and release the iolock before re-raising the exception
                    raise e
                
                outputlock.acquire()
                stdout("[+] doxx: -- " + outfile_path + " ... check")
                outputlock.release()
            except Exception as e:
                outputlock.acquire()
                stderr("[!] doxx: There was a file write error with '" + template_path + "'. Error message: " + str(e), exit=0)
                outputlock.release()
                sys.exit(1)  # release the lock before raising SystemExit
        else:
            # template meta data is in template.meta_data
            # template text is in template.text
            # perform the text replacements:
            try:
                ink_template = InkTemplate(template.text)
                ink_renderer = InkRenderer(ink_template, self.key_data)
                rendered_text = ink_renderer.render()
            except Exception as e:
                outputlock.acquire()
                stderr("[!] doxx: An error occurred during the text replacement attempt.  Error message: " + str(e), exit=0)            
                outputlock.release()
                sys.exit(1)  # release the lock before raising SystemExit
        
            # if the requested destination directory path does not exist, make it
            outfile_dir_path = make_path(os.path.dirname(self.key_path), os.path.dirname(template.outfile))
            try:
                iolock.acquire()
                if not outfile_dir_path == '' and not dir_exists(outfile_dir_path):
                    make_dirs(outfile_dir_path)
                iolock.release()
            except Exception as e:
                outputlock.acquire()
                stderr("[!] doxx: Unable to create directory path '" + outfile_dir_path + "' for your file write. Error: " + str(e), exit=0)
                outputlock.release()
                iolock.release()
                sys.exit(1)  # release the iolock before raising SystemExit
                
            outfile_path = make_path(os.path.dirname(self.key_path), template.outfile)
            
            try:
                iolock.acquire()
                fw = FileWriter(outfile_path)
                fw.write(rendered_text)
                iolock.release()
            except Exception as e:
                outputlock.acquire()
                stderr("[!] doxx: Unable to write the file '" + outfile_path + "'. Error: " + str(e), exit=0)
                outputlock.release()
                iolock.release()
                sys.exit(1)  # release the iolock before raising SystemExit
                
            outputlock.acquire()
            stdout("[+] doxx: -- " + outfile_path + " ... check")
            outputlock.release()
        

    def project_archive_run(self, key):
        try:
            project_path = key.meta_data['project']
            # Remote .tar.gz or .zip project archives
            if is_url(project_path):
                # pull the remote project and unpack it, define the root directory with the returned value from the function
                root_dir = run_pull(project_path)
                
                # make the path to the 'project.yaml' key file
                project_key_path = make_path(root_dir, 'project.yaml')           
                
                if file_exists(project_key_path):
                    self.write_project_runner_key(project_key_path)  # append the key data to the project.yaml key
                else:
                    stderr("[!] doxx: Unable to locate the 'project.yaml' project settings file in your unpacked archive", exit=1)
                
                # instantiate a new Builder object with the updated 'project.yaml' local file
                builder = Builder(project_key_path)
                builder.run()  # build with the updated 'project.yaml' key
            # Local .tar.gz or .zip project archives
            else:
                project_key_path = self.unpack_and_get_keypath(project_path)
                
                # create an updated 'project.yaml' key file from the remote project template paths and the local user key data
                if file_exists(project_key_path):
                    self.write_project_runner_key(project_key_path)
                else:
                    stderr("[!] doxx: Unable to locate the 'project.yaml' project settings file in your unpacked archive", exit=1)
                    
                # instantiate a new Builder object with the updated 'project.yaml' local file
                builder = Builder(project_key_path)
                builder.run()            # build with the updated 'project.yaml' key
                
                # remove the project archive
                os.remove(project_path)
        except Exception as e:
            stderr("[!] doxx: Unable to build from the project archive because of an error.  Error: " + str(e), exit=1)
                
    
    def unpack_and_get_keypath(self, project_path):
        # unpack the archive and get the root directory from the archive
        root_directory = unpack_run(project_path)
        
        if root_directory is None or root_directory == "":
            key_path = None
            try:
                for root, dirs, files in os.path.walk(cwd()):
                    for test_file in files:
                        if test_file == "project.yaml":
                            key_path = make_path(root, dirs, test_file)
            except Exception as e:
                stderr("[!] doxx: Unable to locate the 'project.yaml' project settings file in your unpacked archive. Error: " + str(e), exit=1)
                
            if key_path is None:  # can't find key path
                stderr("[!] doxx: Unable to locate the 'project.yaml' project settings file in your unpacked archive.", exit=1)
            else:
                return key_path  # return key path to the calling method
        else:
            if root_directory == ".":
                key_path = 'project.yaml'  # in current working directory
            else:
                # make the path to the key file
                root_directory = make_path(cwd(), root_directory)
                key_path = make_path(root_directory, 'project.yaml')
            # return the key path to the calling method
            return key_path
        
    
    def write_project_runner_key(self, project_key_path):
        key_data_string = "\n\n"  # maintain a couple of newlines between the build specification section and the key data section
        if len(self.key_data) > 0:
            for the_key in self.key_data:
                key_data_string = key_data_string + the_key + ": " + self.key_data[the_key] + "\n" # recreate the YAML from the local key.yaml file to append to the project.yaml file
        # if there is no key data, not necessary to write any additional data to the file.  when doxx key is instantiated it will handle the lack of replacement data
        
        # append the local key file ('key.yaml') key data to the project meta data to prepare for the build
        try:
            fw = FileWriter(project_key_path)
            fw.append(key_data_string)  # append local key data to the project.yaml file
        except Exception as e:
            stderr("[!] doxx: Unable to write the temporary key file for your project build. Error: " + str(e), exit=1)
        
        
    
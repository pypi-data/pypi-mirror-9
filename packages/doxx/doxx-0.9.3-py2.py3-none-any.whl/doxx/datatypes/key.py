#!/usr/bin/env python
# encoding: utf-8

import os
import unicodedata
from Naked.toolshed.file import FileReader
from Naked.toolshed.system import directory, make_path
from Naked.toolshed.system import file_exists, stderr
from Naked.toolshed.python import is_py2
from yaml import load_all
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class DoxxKey(object):
    def __init__(self, inpath):
        # instance variables
        self.meta_data = {}      # holds key meta data (template or templates keys)
        self.key_data = {}       # holds key data (user specified keys)
        self.key_path = inpath
        self.no_replacements = False     # changed to True in _read_yaml if there are no replacement string keys included
        self.single_template_key = False  # changed to True in teh _generate_dir_paths method if 'template' in meta data
        self.multi_template_key = False  # changed to True in the _generate_dir_paths method if 'templates' detected in meta data
        self.project_key = False  # changed to True in the _generate_dir_paths method if 'project' detected in meta data
        self.github_repo_key = False
        self.textfile_key = False
        self.binaryfile_key = False
        
        # define instance variables on object instantiation
        self._read_yaml(inpath)  # define self.meta_data & self.key_data with the yaml key file
        self._cast_values_to_unicode()  # cast non-string values to strings (necessary for the Ink Renderer class)
        self._generate_dir_path(inpath)  # join the directory path to the template files specified in the key (for keys executed from outside of containing directory)
        
        # confirm the integrity of the key file
        self._parse_yaml_for_errors()
    
    def _read_yaml(self, inpath):
        """local YAML doxx key file reader (private method)"""
        if file_exists(inpath):
            fr = FileReader(inpath)
            the_yaml = fr.read()  # FileReader reads in utf-8 encoded bytes data
            the_data = load_all(the_yaml, Loader=Loader)
            i = 0
            for x in the_data:
                if i == 0:
                    # first section of the YAML is meta data
                    self.meta_data = x
                elif i == 1:
                    # second section of the YAML includes the key data
                    self.key_data = x
                else:
                    pass  # ignore any other sections that are included
        
                i += 1  # used to iterate through the_data
            # define the no replacements attribute as True if there is no key data
            if self.key_data is None:
                self.no_replacements = True
        else:
            stderr("[!] doxx: Unable to load the requested key " + inpath + ". Please check the path and try again.", exit=1)
            
                    
    def _cast_values_to_unicode(self):
        unicode_key_data_dict = {}  # new dictionary that will contain the UTF-8 encoded unicode keys and values from self.key_data
        if self.key_data is None or len(self.key_data) == 0:
            key_list = []
        else:
            key_list = self.key_data.keys()
            
        for key in key_list:
            unicode_key = unicodedata.normalize('NFKD', self._create_python_dependent_unicode(key))                    # encode the key
            if self.key_data[key] == None:
                unicode_value = unicodedata.normalize('NFKD', self._create_python_dependent_unicode(""))              # if value == None (i.e. key present but no definition included), replace with empty string = empty string replacement
            else:
                unicode_value = unicodedata.normalize('NFKD', self._create_python_dependent_unicode(self.key_data[key]))  # otherwise normalize it
            unicode_key_data_dict[unicode_key] = unicode_value       # assign the encoded values to the new dictionary
        
        self.key_data = unicode_key_data_dict     # define the instance key_data with the new unicode encoded keys and values
                
    
    def _create_python_dependent_unicode(self, unknown_encoding_string):
        if is_py2():  # python 2 only 
            if isinstance(unknown_encoding_string, unicode):    # test for Python 2 unicode type
                return unknown_encoding_string                  # it is already unicode, just return it
            else:
                return unicode(unknown_encoding_string)         # otherwise, cast to unicode
        else:  # python 3 only
            if isinstance(unknown_encoding_string, str):
                return unknown_encoding_string                  # return unmodified string, py3 strings are unicode by default
            else:
                return str(unknown_encoding_string)             # convert to utf-8 encoded string   
    
    
    def _generate_dir_path(self, inpath):
        """joins the directory path from the current working directory to the template file paths specified in the doxx key meta data (private method)"""
        if self.meta_data is None:
            meta_keys = []
        else:
            meta_keys = self.meta_data.keys()
        
        if 'template' in meta_keys and self.meta_data['template'] is not None:     # single template file request
            self.single_template_key = True                                        # single template key property set to True
            pre_file_path = self.meta_data['template']
            if len(pre_file_path) > 6 and (pre_file_path[0:7] == "http://" or pre_file_path[0:8] == "https://"):  # not necessary to build new path if it is a URL
                pass
            else:
                dir_path = directory(inpath)
                # create OS specific path string from the user entered value in 'template:' field
                os_specific_filepath = self.normalize_filepath(pre_file_path)
                self.meta_data['template'] = make_path(dir_path, os_specific_filepath)
        elif 'templates' in meta_keys:  # multi-template file request
            self.multi_template_key = True  # used to detect whether there is a need to process multiple templates with this key
            i = 0  # used for the templates list key during the new path join in following block
            for template in self.meta_data['templates']:  # iterate through template files and join the directory path to the specified template path
                if template == '':
                    pass  # do nothing if it is an empty string, check will be performed in _parse_yaml_for_errors method below.
                else:
                    pre_file_path = template
                    if len(pre_file_path) > 6 and (pre_file_path[0:7] == "http://" or pre_file_path[0:8] == "https://"):  # not necessary to build new path if it is a URL
                        pass
                    else:
                        dir_path = directory(inpath)
                        # create OS specific path string from the user entered values in the 'templates:' field
                        os_specific_filepath = self.normalize_filepath(pre_file_path)
                        self.meta_data['templates'][i] = make_path(dir_path, os_specific_filepath)
                i += 1
        elif 'project' in meta_keys and not self.meta_data['project'] == None:
            self.project_key = True  # indicate that this is a key that uses a project file
            pre_file_path = self.meta_data['project']
            if len(pre_file_path) > 6 and (pre_file_path[0:7] == "http://" or pre_file_path[0:8] == "https://"):  # not necessary to build new path if it is a URL
                pass
            else:
                dir_path = directory(inpath)
                # create OS specific path string from the user entered value in the 'project:' field
                os_specific_filepath = self.normalize_filepath(pre_file_path)
                self.meta_data['project'] = make_path(dir_path, os_specific_filepath)
        else:
            pass  # if the meta data is missing, the check will be performed in the _parse_yaml_for_errors method below. do nothing here
        
        # Github repository request property definitions in the Key
        if 'github-repos' in meta_keys and not self.meta_data['github-repos'] == None:
            self.github_repo_key = True  # used in build command processing
        if 'textfiles' in meta_keys and not self.meta_data['textfiles'] == None:
            self.textfile_key = True
        if 'binaryfiles' in meta_keys and not self.meta_data['binaryfiles'] == None:
            self.binaryfile_key = True       

        
    def normalize_filepath(self, pre_filepath):
        """returns a filepath with the correct OS-dependent path separators"""
        return os.path.normpath(pre_filepath)    
    
    
    def _parse_yaml_for_errors(self):
        # confirm that there are key data
        # confirm that the meta data are complete
        test_meta_data = self.meta_data
        if test_meta_data is None:
            test_metadata_keys = []
        else:
            test_metadata_keys = self.meta_data.keys()
            
        # missing metadata
        if len(test_metadata_keys) == 0:
            stderr("[!] doxx: The build specification header is missing from your key file.  Please include your template or project file path(s).", exit=1)
        
        # test for absence of all appropriate build spec field types
        if 'template' not in test_metadata_keys:
            if 'templates' not in test_metadata_keys:
                if 'project' not in test_metadata_keys:
                    if 'github-repos' not in test_metadata_keys:
                        if 'textfiles' not in test_metadata_keys:
                            if 'binaryfiles' not in test_metadata_keys:
                                stderr("[!] doxx: There are no template or project files specified in your key. Please complete the build specification section at the head of your key file.", exit=1)
            
        # TOO MANY FIELDS
        # meta data contains both template and templates fields test
        if 'template' in test_metadata_keys and 'templates' in test_metadata_keys:
            stderr("[!] doxx: The 'template' and 'templates' fields are both included in your key file.  Please remove one field and run your command again.", exit=1)
            
        # meta data contains both project and template fields test
        if 'project' in test_metadata_keys and 'template' in test_metadata_keys:
            stderr("[!] doxx: The 'template' and 'project' fields are both included in your key file.  Please remove one field and run your command again.", exit=1)
            
        # meta data contains both project and templates fields test
        if 'project' in test_metadata_keys and 'templates' in test_metadata_keys:
            stderr("[!] doxx: The 'templates' and 'project' fields are both included in your key file.  Please remove one field and run your command again.", exit=1)
            
        # UNDEFINED TEMPLATES
        # meta data template field does not include a template path value
        if 'template' in test_metadata_keys and test_meta_data['template'] == None:
            stderr("[!] doxx: The template field in your key does not include a template path. Please include a path to your template file.", exit=1)
            
        # meta data templates field does not include template paths
        if 'templates' in test_metadata_keys and (test_meta_data['templates'] == None or len(test_meta_data['templates']) == 0):
            stderr("[!] doxx: The templates field in your key does not include template paths.  Please include paths to your template files.", exit=1)
        
        # meta data project field does not include a template path value
        if 'project' in test_metadata_keys and test_meta_data['project'] == None:
            stderr("[!] doxx: The project field in your key is empty. Please include a path to your template file.", exit=1)     
            
        # meta data templates field includes an empty string file path
        if 'templates' in test_metadata_keys:
            for template in test_meta_data['templates']:
                if template == '':
                    stderr("[!] doxx: The templates field in your key file contains an empty file path.  Please fix this and try again.", exit=1)
                    
                    
                    
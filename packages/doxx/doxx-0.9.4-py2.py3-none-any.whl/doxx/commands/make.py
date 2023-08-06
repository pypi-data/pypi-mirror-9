#!/usr/bin/env python
# encoding: utf-8

import os
from Naked.toolshed.file import FileWriter
from Naked.toolshed.system import stdout, stderr, file_exists, dir_exists

###############
# KEY.YAML STUB - changes to this stub require changes to the datatypes.key._parse_yaml_for_errors method
###############

key_stub = """
---

# Key file documentation: http://doxx.org/usage/keys/

###################################################
# Exclusive build specification fields (choose one)
###################################################

template: ***.doxt
templates: [***.doxt, 'http://***/***.doxt']
project: ***.tar.gz


#####################################################
# Non-exclusive build specification fields (optional)
#####################################################

textfiles:
    localfile.txt: "https://files.com/some/great/file.txt"
    localfile2.txt: ""https://files.com/some/great/file2.txt"

---

# Enter the key for the available template replacement strings below (YAML syntax):
"""


###################
# PROJECT.YAML STUB - changes to this stub require changes to the datatypes.key._parse_yaml_for_errors method
###################

project_yaml_stub = """
---

# Project archive documentation: http://doxx.org/usage/archives/

###################################################
# Exclusive build specification fields (choose one)
###################################################

template: ***.doxt
templates: [***.doxt, 'http://***/***.doxt']


#####################################################
# Non-exclusive build specification fields (optional)
#####################################################

textfiles:
    localfile.txt: "https://files.com/some/great/file.txt"
    localfile2.txt: ""https://files.com/some/great/file2.txt"

---
"""

##################
# TEMPLATE STUB
##################

template_stub = """
---doxx---

# Template file documentation: http://doxx.org/usage/templates/

# (REQUIRED) enter the file extension for file rendered from this template, leave blank for no extension
#  the use of a '.' in the extension definition is optional (e.g. you can use '.txt' or 'txt')
extension:

# (OPTIONAL) enter a base file name for files generated from this template:
#  default: absent or undefined = use the template base file name for the generated file
basename:

# (OPTIONAL) enter a sub-directory path relative to the KEY FILE for the template file build
#  default : absent or undefined = write to root directory where the user's key file is located
destination-directory:

# (OPTIONAL): change to 'true' for verbatim template writes (i.e. no text replacements)
#  default: false or absent = attempt text replacements in this template file
verbatim: false

---doxx---

"""

### END TEMPLATE STUB


class Maker(object):
    """doxx key, template, and project stub generator class"""
    def __init__(self):
        pass
    
    def make_key(self, outpath):
        try:
            fw = FileWriter(outpath)
            fw.write(key_stub)
            if file_exists(outpath):
                stdout("[+] doxx: The key stub '" + outpath + "' is now available in the current directory.")
        except Exception as e:
            stderr("[!] doxx: Unable to write the key stub to disk.  Error: " + str(e), exit=1)
        
    def make_template(self, outpath):
        try:
            fw = FileWriter(outpath)
            fw.write(template_stub)
            if file_exists(outpath):
                stdout("[+] doxx: The template stub '" + outpath + "' is now available in the current directory.")
        except Exception as e:
            stderr("[!] doxx: Unable to write the template stub to disk. Error: " + str(e), exit=1)
            
    def make_project(self):
        try:
            # project.yaml file write
            fw_projyaml = FileWriter('project.yaml')
            fw_projyaml.write(project_yaml_stub)
            
            # pkey.yaml file write
            fw_pkey = FileWriter('pkey.yaml')
            fw_pkey.write(key_stub)
            
            # templates directory write
            if not dir_exists('templates'):
                os.mkdir('templates')
                
            # template.doxt file in templates directory
            template_stub_path = os.path.join('templates', 'stub.doxt')
            fw_template = FileWriter(template_stub_path)
            fw_template.write(template_stub)
            
            # confirm for user
            if file_exists('project.yaml'):
                stdout("[+] doxx: 'project.yaml' ... check")
            else:
                stderr("[!] doxx: There was an error writing the 'project.yaml' key file to your project directory")
                
            if file_exists('pkey.yaml'):
                stdout("[+] doxx: 'pkey.yaml' ... check")
            else:
                stderr("[!] doxx: There was an error writing the 'pkey.yaml' key file to your project directory")
                
            if file_exists(template_stub_path):
                stdout("[+] doxx: '" + template_stub_path + "' ... check")
            else:
                stderr("[!] doxx: There was an error writing the '" + template_stub_path + "' template file to your project directory")
        except Exception as e:
            stderr("[!] doxx: Unable to write project files to disk.  Error: " + str(e), exit=1)
            
        

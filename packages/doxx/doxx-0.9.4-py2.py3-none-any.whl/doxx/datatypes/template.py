#!/usr/bin/env python
# encoding: utf-8

from os.path import basename, splitext, normpath
from Naked.toolshed.file import FileReader
from Naked.toolshed.network import HTTP
from Naked.toolshed.system import make_path

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
    

class DoxxTemplate(object):
    """A doxx template class that maintains state of user designed templates during the rendering process"""
    def __init__(self, inpath):
        self.inpath = inpath
        self.raw_text = ""
        self.text = ""
        self.meta_data = {}     # holds meta data from the header of the file
        self.verbatim = False   # should file write take place verbatim (without text replacements), default False, changed to True by user meta data verbatim field
        self.extension = ""     # stored in the format '.txt'
        self.basename = ""      # base filename for the out write file path
        self.outfile = ""       # write file path for use by calling code
    
    def load_data(self):
        fr = FileReader(self.inpath)
        self.raw_text = fr.read()

    def split_data(self):
        parsed_text = self.raw_text.split("---doxx---")

        if len(parsed_text) == 3:  # should split into three sections (0 = before first ---doxx---, 1 = meta data, 2 = template text data after second ---doxx---)
            self.meta_data = load(parsed_text[1], Loader=Loader)
            self.text = parsed_text[2][1:]  # define self.text with the template data from the file, the [1:] slice removes /n at end of the delimiter        
        else:
            self.meta_data = {}
            self.text = u""
    
    def parse_template_text(self):
        """parses doxx template meta data YAML and main body text and defines instance variables for the DoxxTemplate (public method)"""

        meta_keys = self.meta_data.keys()

        # if user did not enter an extension type, 
        if 'extension' not in meta_keys or self.meta_data['extension'] == None:
            self.extension = ""  # default to no extension if user did not enter the meta data field, or the meta data field has no definition
        else:
            self.extension = self.meta_data['extension']  # define the instance extension attribute with the value from the template meta data
        
        # define rendered file destination directory relative to current working directory
        if 'destination_directory' not in meta_keys or self.meta_data['destination_directory'] == None:
            dest_dir = u""
        else:
            # replace user entered path with OS specific separators and re-define the destination directory attribute
            self.meta_data['destination_directory'] = self.normalize_filepath(self.meta_data['destination_directory'])
            dest_dir = self.meta_data['destination_directory']

        # define rendered file extension as instance attribute
        if len(self.extension) > 0:  # if no extension (user did not enter extension field or did not define an extension), then skip '.' check
            if self.extension[0] == ".":
                pass
            else:
                self.extension = "." + self.extension  # add a period if the user did not include it

        # define rendered file base file name (different approach for local vs. remote paths)
        if 'basename' not in meta_keys or self.meta_data['basename'] == None:
            # if it is a URL, split by '/' and obtain file path from the URL
            if len(self.inpath) > 6 and (self.inpath[0:7] == "http://" or self.inpath[0:8] == "https://"):
                url_path = self.inpath.split("/")
                filename_with_extension = splitext(url_path[-1])  # get the filename from the '/' split url :: url_path[-1] = URL filename, [0] index is the basename from that filename.extension
                self.basename = filename_with_extension[0]
            else:  # local files
                self.basename = splitext(basename(self.inpath))[0]
        else:
            self.basename = self.meta_data['basename']

        file_name = self.basename + self.extension  # local temp file_name variable, modified below to final write path

        # make the outfile path to be used for the rendered file write
        if len(dest_dir) > 0:
            self.outfile = make_path(dest_dir, file_name)
        else:
            self.outfile = file_name
        
        # test for user request to write the file out verbatim, skips the text replacement step during the build
        if 'verbatim' in meta_keys and self.meta_data['verbatim'] == True:
            self.verbatim = True
        else:
            self.meta_data['verbatim'] = False
            # self.verbatim is False by default, define the meta_data key with False value in case user included it without definining it

    def parse_template_for_errors(self):
        """evaluates template file for presence of meta data header and template text.  Returns a two-tuple. tuple[0] = True if error identified, False if error not identified.  tuple[1] = error message string"""
        # confirm meta data contains data
        if self.meta_data is None or len(self.meta_data) == 0:
            error_message = u"[!] doxx: The template file '" + self.inpath + "' is not properly formatted.  Please include the required build specification block between '---doxx---' delimiters at the top of your file."
            return (True, error_message)
        # confirm that there is template text
        elif self.text is None or len(self.text) < 5:  # if self.text not defined or length of the string < 5 chars (because {{x}} == 5 so must not include any replacement tags)
            error_message = u"[!] doxx: Unable to parse template text from the template file '" + self.inpath + "'. Please include a template in order to render this file."
            return (True, error_message)
        else:
            return(False, "no message")
        

    def normalize_filepath(self, pre_filepath):
        """returns a filepath with the correct OS-dependent path separators"""
        return normpath(pre_filepath)  



class RemoteDoxxTemplate(DoxxTemplate):
    def __init__(self, inpath):
        DoxxTemplate.__init__(self, inpath)

    def load_data(self):
        """overloaded load_data method that retrieves data from a remote file using HTTP or HTTPS protocol instead of a local file"""
        http = HTTP(self.inpath)
        
        if http.get_status_ok():
            import unicodedata
            norm_text = unicodedata.normalize('NFKD', http.res.text)  # normalize unicode data to NFKD (like local file reads)
            self.raw_text = norm_text
            return (True, "no message")
        else:
            fail_status_code = http.res.status_code
            error_message = "[!] doxx: Unable to load the remote template file '" + self.inpath + "' (HTTP status code " + str(fail_status_code) + ")"
            return (False, error_message)
            
        
        
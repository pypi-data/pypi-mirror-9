#!/usr/bin/env python
# encoding: utf-8


class OfficialPackage(object):
    def __init__(self):
        self.binary_package_url_prefix = "https://github.com/doxx-repo/"
        self.binary_package_url_postfix = "/releases/download/current/"
        self.package_key_file_url_prefix = "https://github.com/doxx-repo/"
        self.package_key_file_url_postfix = "/releases/download/current/pkey.yaml"
        
        self.master_package_list_text_url = "https://doxx-cdn.s3.amazonaws.com/list.txt"
        self.master_package_description_json_url = "https://doxx-cdn.s3.amazonaws.com/packages.json"
        
        # Release file URL's
        # https://github.com/doxx-repo/{package-name}/releases/download/current/{package-name}.tar.gz
        # https://github.com/doxx-repo/{package-name}/releases/download/current/{package-name}.zip
        # https://github.com/doxx-repo/{package-name}/releases/download/current/pkey.yaml
    
    # Attribute getter methods
    
    def get_package_targz_url(self, package_name):
        normalized_package_name = package_name.lower().strip()
        return self.binary_package_url_prefix + normalized_package_name + self.binary_package_url_postfix + normalized_package_name + '.tar.gz'
    
    def get_package_zip_url(self, package_name):
        normalized_package_name = package_name.lower().strip()
        return self.binary_package_url_prefix + normalized_package_name + self.binary_package_url_postfix + normalized_package_name + '.zip'     
    
    def get_package_key_url(self, package_name):
        normalized_package_name = package_name.lower().strip()
        return self.package_key_file_url_prefix + normalized_package_name + self.package_key_file_url_postfix
    
    def get_master_package_list_url(self):
        return self.master_package_list_text_url
    
    def get_master_package_description_json_url(self):
        return self.master_package_description_json_url
    

    
    
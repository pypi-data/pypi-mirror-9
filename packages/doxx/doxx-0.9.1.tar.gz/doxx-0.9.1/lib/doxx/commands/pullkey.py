#!/usr/bin/env python
# encoding: utf-8

from Naked.toolshed.file import FileWriter
from Naked.toolshed.network import HTTP
from Naked.toolshed.system import stdout, stderr
from doxx.datatypes.package import OfficialPackage


def run_pullkey(package_name):
    normalized_package_name = package_name.lower().strip()
    package = OfficialPackage()
    key_file_url = package.get_package_key_url(normalized_package_name)
    try:
        stdout("[*] doxx: Pulling the remote key file...")
        http = HTTP(key_file_url)
        if http.get_status_ok():
            key_file_text = http.res.text
            fr = FileWriter('key.yaml')
            try:
                fr.write(key_file_text)
            except Exception as e:
                stderr("[!] doxx: Unable to write the 'key.yaml' file to disk. Error: " + str(e), exit=1)
            stdout("[*] doxx: Key file pull complete")
        elif http.res.status_code == 404:
            stderr("[!] doxx: Unable to pull the key file because the requested package could not be found. (HTTP status code: 404)", exit=1)
        else:
            stderr("[!] doxx: Unable to pull the key file.  (HTTP status code: " + str(http.res.status_code) + ")", exit=1)
    except Exception as e:
        stderr("[!] doxx: Unable to pull the key file. Error: " + str(e), exit=1)
        
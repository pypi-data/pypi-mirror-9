#!/usr/bin/env python
# encoding: utf-8

#------------------------------------------------------------------------------
# doxx
# Copyright 2015 Christopher Simpkins
# MIT license
#------------------------------------------------------------------------------

# Application start
def main():
    import sys
    from os.path import basename
    from Naked.commandline import Command
    from Naked.toolshed.system import stdout, stderr, is_dir, is_file, cwd
    from doxx.commands.build import Builder
    from doxx.commands.make import Maker

    #------------------------------------------------------------------------------------------
    # [ Instantiate command line object ]
    #   used for all subsequent conditional logic in the CLI application
    #------------------------------------------------------------------------------------------
    c = Command(sys.argv[0], sys.argv[1:])
    #------------------------------------------------------------------------------------------
    # [ Command Suite Validation ] - early validation of appropriate command syntax
    # Test that user entered at least one argument to the executable, print usage if not
    #------------------------------------------------------------------------------------------
    if not c.command_suite_validates():
        from doxx.settings import usage as doxx_usage
        print(doxx_usage)
        sys.exit(1)
    #------------------------------------------------------------------------------------------
    # [ NAKED FRAMEWORK COMMANDS ]
    # Naked framework provides default help, usage, and version commands for all applications
    #   --> settings for user messages are assigned in the lib/doxx/settings.py file
    #------------------------------------------------------------------------------------------
    if c.help():      # User requested doxx help information
        from doxx.settings import help as doxx_help
        print(doxx_help)
        sys.exit(0)
    elif c.usage():   # User requested doxx usage information
        from doxx.settings import usage as doxx_usage
        print(doxx_usage)
        sys.exit(0)
    elif c.version():   # User requested doxx version information
        from doxx.settings import app_name, major_version, minor_version, patch_version
        version_display_string = app_name + ' ' + major_version + '.' + minor_version + '.' + patch_version
        print(version_display_string)
        sys.exit(0)
    #------------------------------------------------------------------------------------------
    # [ PRIMARY COMMAND LOGIC ]
    #   Enter your command line parsing logic below
    #------------------------------------------------------------------------------------------
    elif c.cmd == "build":
        if c.argc > 1:
            key_path = c.arg1
        else:
            key_path = "key.yaml"
        stdout("[*] doxx: Build started with the key file '" + key_path + "'...")
        b = Builder(key_path)
        b.run()
        stdout("[*] doxx: Build complete.")
    elif c.cmd == "browse":
        from doxx.commands.browse import browse_docs
        if c.argc > 1:
            query = c.arg1
            browse_docs(query)
        else:
            # default to open the main documentation page
            query = "docs"
            browse_docs(query)
    elif c.cmd == "clean":
        from doxx.commands.clean import run_clean
        run_clean()  # execute the clean routines
    elif c.cmd == "make":
        if c.argc > 1:
            if c.cmd2 == "key":  # secondary command        
                m = Maker()
                if c.argc > 2:
                    m.make_key(c.arglp)
                else:
                    m.make_key("key.yaml")
            elif c.cmd2 == "template":  # secondary command
                m = Maker()
                if c.argc > 2:
                    m.make_template(c.arglp)
                else:
                    m.make_template("stub.doxt")  # default name is 'stub.doxt' for new template if not specified by user
            elif c.cmd2 == "project":
                m = Maker()
                m.make_project()
            else:
                stderr("Usage: doxx make [key|project|template]", exit=1)
        else:
            stderr("[!] doxx: Please include the secondary command 'key', 'project', or 'template' with the 'make' command.", exit=1)
    elif c.cmd == "pack":
        from doxx.commands.pack import tar_gzip_package_directory, zip_package_directory 
        if c.argc > 1:
            if c.cmd2 == "zip":
                if c.argc > 2:  # request for zip with a directory path
                    if is_dir(c.arglp):
                        zip_package_directory(c.arglp, c.arglp)
                    else:
                        stderr("[!] doxx: '" + c.arglp + "' does not appear to be a directory.  Please enter the path to your project directory.", exit=1)
                else:  # request for zip with current working directory
                    stderr("[!] doxx: Please include your project directory as an argument to the zip command", exit=1)
            else:  # request for tar.gz with a directory path
                if is_dir(c.arglp):
                    tar_gzip_package_directory(c.arglp, c.arglp)
                else:
                    stderr("[!] doxx: '" + c.arglp + "' does not appear to be a directory.  Please enter the path to your project directory.", exit=1)
        else:  # request for tar.gz in current working directory
            root_dir = cwd()
            archive_name = basename(root_dir)
            tar_gzip_package_directory(archive_name, root_dir)
        # end of the pack command
        stdout("[*] doxx: Pack complete")
    elif c.cmd == "pull":
        if c.argc > 1:
            from doxx.commands.pull import run_pull
            run_pull(c.arg1)
            stdout("[*] doxx: Pull complete")
        else:
            stderr("[!] doxx: Please include the URL for the archive that you would like to pull.", exit=1)
    elif c.cmd == "pullkey":
        if c.argc > 1:
            from doxx.commands.pullkey import run_pullkey
            run_pullkey(c.arg1)
        else:
            stderr("[!] doxx: Please include a package name with the pullkey command", exit=1)
    elif c.cmd == "search":
        if c.argc > 1:
            from doxx.commands.search import run_search
            run_search(c.arg1)
        else:
            stderr("[!] doxx: Please include a search string after your command.", exit=1)
    elif c.cmd == "unpack":
        if c.argc > 1:
            if is_file(c.arg1):
                from doxx.commands.unpack import unpack_run, remove_compressed_archive_file
                unpack_run(c.arg1)
                remove_compressed_archive_file(c.arg1)
                stdout("[*] doxx: Unpack complete")
            else:
                stderr("[!] doxx: '" + c.arg1 + "' does not appear to be a file.  Please include a path to your compressed file.", exit=1)
        else:
            stderr("[!] doxx: Please include a path to your file.", exit=1)
    elif c.cmd == "whatis":
        if c.argc > 1:
            from doxx.commands.whatis import run_whatis
            run_whatis(c.arg1)
        else:
            stderr("[!] doxx: Please enter a package name following your command.", exit=1)
    #------------------------------------------------------------------------------------------
    # UNDOCUMENTED TESTING COMMANDS
    #  
    #------------------------------------------------------------------------------------------    
    elif c.cmd == "repoupdate":
        from doxx.commands.repoupdate import run_repoupdate
        run_repoupdate()
    
    #------------------------------------------------------------------------------------------
    # [ DEFAULT MESSAGE FOR MATCH FAILURE ]
    #  Message to provide to the user when all above conditional logic fails to meet a true condition
    #------------------------------------------------------------------------------------------
    else:
        stderr("[!] doxx: Could not complete the command that you entered.  Please try again.")
        sys.exit(1) #exit

if __name__ == '__main__':
    main()
    
    
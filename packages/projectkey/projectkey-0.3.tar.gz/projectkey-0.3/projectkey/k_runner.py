#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import os, imp, inspect
from interpreter import cli_interface

def k_runner():
    """CLI interpreter for the k command."""
    # Check every directory from the current all the way to / for a file named key.py
    checkdirectory = os.getcwd()
    directories_checked = []
    keypy_filename = None
    while not os.path.ismount(checkdirectory):
        directories_checked.append(checkdirectory)
        if os.path.exists("{0}{1}key.py".format(checkdirectory, os.sep)):
            keypy_filename = "{0}{1}key.py".format(checkdirectory, os.sep)
            break
        else:
            checkdirectory = os.path.abspath(os.path.join(checkdirectory, os.pardir))

    if not keypy_filename:
        print "key.py not found in the following directories:\n"
        print '\n'.join(directories_checked)
        print "\nSee http://projectkey.readthedocs.org/en/latest/quickstart.html"
        return 1
    else:
        cli_interface(imp.load_source("key", keypy_filename))
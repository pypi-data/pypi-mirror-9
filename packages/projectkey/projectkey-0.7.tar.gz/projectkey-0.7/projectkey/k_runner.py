#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import interpreter
import inspect
import imp
import sys
import os


def k_runner():
    """k command handler - searcher of the key.py file before handing over control to the CLI."""
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
        sys.stderr.write("key.py not found in the following directories:\n\n")
        sys.stderr.write('\n'.join(directories_checked))
        sys.stderr.write("\n\nSee http://projectkey.readthedocs.org/en/latest/quickstart.html\n")
        sys.exit(1)
    else:
        interpreter.cli(imp.load_source("key", keypy_filename))

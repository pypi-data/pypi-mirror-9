#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
from run_commands import run_return
from run_commands import run
import interpreter
import subprocess
import k_runner
import sys
import os


# The version as used in the setup.py and the docs conf.py
__version__ = "0.7"

# Because most key.py file users will want to change directory at some point
cd = os.chdir

def ignore_ctrlc(method):
    """Decorator to make a ProjectKey command ignore Ctrl-C.
       - For a commands that runs programs that want to handle
         Ctrl-C themselves - ipython for instance."""
    method.ignore_ctrlc = True
    return method

def runnable(name):
    """Makes a key.py file runnable directly (as well as through the k command)."""
    if name == '__main__':
        interpreter.cli(sys.modules[name])
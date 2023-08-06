#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import k_runner, interpreter, os, subprocess, sys

# The version as used in the setup.py and the docs conf.py
__version__ = "0.3"

cli = interpreter.cli_interface
cd = os.chdir

def run(shell_commands, ignore_errors=True):
    """Run shell commands."""
    try:
        for shell_command in shell_commands.split('\n'):
            subprocess.check_call(shell_command, shell=True)
    except subprocess.CalledProcessError, error:
        if error.output is not None:
            sys.stderr.write(error.output)
        if not ignore_errors:
            sys.exit(1)

def run_return(shell_command):
    """Run shell commands and return the output."""
    return subprocess.check_output(shell_command, shell=True)

def runnable(name):
    """Makes a key.py file runnable directly (as well as through the k command)."""
    if name == '__main__':
        interpreter.cli_interface(sys.modules[name])

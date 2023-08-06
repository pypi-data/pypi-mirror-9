from __future__ import print_function
import os, sys, command_class
import argcomplete, argparse

def cli_interface(projectkey_module):
    """CLI interpreter for the ProjectKey."""
    cc = command_class.CommandClass(projectkey_module)
    parser = argparse.ArgumentParser(add_help=False, prefix_chars=[None,])
    parser.add_argument("commands", nargs='*', default=None).completer = cc.command_completer
    argcomplete.autocomplete(parser)
    commands = parser.parse_args().commands
    returnval = 0

    if len(commands) == 0 or len(commands) == 1 and commands[0] in ['-h', '--help', 'help']:
        print("Usage: k command [args]\n")
        if cc.doc() is not None:
            print("%s\n" % cc.doc())
        print(cc.commands_help())
        print("Run 'd help [command]' to get more help on a particular command.")
    elif len(commands) > 1 and commands[0] in ['-h', '--help', 'help']:
        command = commands[1]
        if command in cc.command_list():
            print("Usage: k %s %s" % (command, cc.arg_help(command)))
            print()
            print(cc.commands[command]['helptext'])
        else:
            print("Command '%s' not found in %s. Type 'd help' to see a full list of commands." % (command, cc.projectkey_file))
    else:
        returnval = cc.run_command(commands[0], commands[1:])

    sys.exit(returnval)

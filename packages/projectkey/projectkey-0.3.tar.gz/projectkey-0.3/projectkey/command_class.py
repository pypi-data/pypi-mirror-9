import os, inspect, sys

class CommandClass(object):
    def __init__(self, projectkey_module):
        self.projectkey_module = projectkey_module
        self.projectkey_file = inspect.getfile(self.projectkey_module)

        self.commands = {}
        for method_name, actual_method in inspect.getmembers(self.projectkey_module, inspect.isfunction):
            if not method_name.startswith("_") and inspect.getmodule(actual_method) == self.projectkey_module:
                docstring = "" if actual_method.__doc__ is None else actual_method.__doc__
                argspec = inspect.getargspec(actual_method)
                args = argspec.args[1:]
                varargs = argspec.varargs
                keyargs = argspec.keywords
                defaults = argspec.defaults

                if varargs is not None and keyargs is not None:
                    sys.stderr.write("Method '%s' in key.py cannot have both *args and **kwargs.\n" % method_name)
                    sys.exit(1)

                minargs = maxargs = 0
                if varargs is not None or keyargs is not None:
                    maxargs = 1024
                    minargs = len(args)
                    argdocs = ['[%s1]' % varargs[:-1], '[%s2]' % varargs[:-1], '[%s3]' % varargs[:-1], '...',]
                else:
                    maxargs = len(args)
                    if defaults is not None:
                        minargs = len(args) - len(defaults)
                        argdocs = ['%s' % x for x in args[:minargs]] + ['[%s]' % x for x in args[minargs:]]
                    else:
                        minargs = len(args)
                        argdocs = ['%s' % x for x in args]
                
                self.commands[method_name] = {
                    'helptext': docstring,
                    'onelinehelp': docstring.split('\n')[0],
                    'function': actual_method,
                    'linenumber': inspect.findsource(actual_method)[1],
                    'minargs': minargs,
                    'maxargs': maxargs,
                    'argdocs': argdocs,
                }

    def doc(self):
        return self.projectkey_module.__doc__

    def arg_help(self, command):
        return ' '.join(self.commands[command]['argdocs'])

    def command_list(self):
        return self.commands.keys()

    def command_completer(self, prefix, parsed_args, **kwargs):
        existing_commands = parsed_args.commands
        if len(existing_commands) == 0:
            return (v for v in self.command_list() + ['help'] if v.startswith(prefix)) 
        else:
            if existing_commands[0] in ["help", "--help", "-h"]:
                return (v for v in self.command_list() + ['help'] if v.startswith(prefix))

    def sorted_commands(self):
        return sorted(self.commands.items(), key=lambda command: command[1]['linenumber'])

    def length_of_longest_command(self):
        return sorted([len(name) for name, _ in list(self.commands.items())], reverse=True)[0]

    def commands_help(self):
        cl = ""
        for name, command in self.sorted_commands():
            if command['helptext']:
                cl = cl + "  %s - %s\n" % (name.rjust(self.length_of_longest_command()), command['onelinehelp'])
        return cl

    def run_command(self, command, command_args):
        """Run a ProjectKey command with a list of command_args."""
        if command in self.command_list():
            if self.commands[command]['minargs'] <= len(command_args) <= self.commands[command]['maxargs']:
                # Feed module the relevant directories
                self.projectkey_module.KEYDIR = os.path.abspath(os.path.dirname(self.projectkey_file))
                self.projectkey_module.CWD = os.getcwd()

                # Run command
                returnvalue = getattr(self.projectkey_module, command)(*command_args)
                
                # If command returns something, print it
                if returnvalue is not None:
                    sys.stdout.write("{0}\n".format(returnvalue))
            else:
                sys.stderr.write("Incorrect number of arguments for command '%s'.\n" % command)
                sys.stderr.write("Arguments used: \"%s\"\n" % ', '.join(command_args))
                return 1
        else:
            sys.stderr.write("Command '%s' not found in %s\n" % (command, self.projectkey_file))
            return 1

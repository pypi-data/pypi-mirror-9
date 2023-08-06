import subprocess


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
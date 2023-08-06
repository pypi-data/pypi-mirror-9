ProjectKey
==========

ProjectKey is a framework to let you write a self-documenting suite of commands in
python to automate common project tasks.

You can then run these commands from any folder inside your project by using the 'k'
key.

For example::

    $ k help
    Usage: k command [args]
    
    Yourproject development environment commands.
    
                    runserver - Run django debug web server on port 8000
                      upgrade - pip upgrade on all packages and freeze to requirements afterwards.
                         smtp - Run development smtp server on port 25025.
      striptrailingwhitespace - strip the trailing whitespace from all files in your mercurial repo.
                  inspectfile - Inspect file(s) for pylint violations.
    
    Run 'k help [command]' to get more help on a particular command.


Three Step Quickstart
=====================

Step 1: Install like so: "sudo pip install projectkey ; sudo activate-global-python-argcomplete"

Step 2: Create a key.py file in the *root* folder of your project like this::
    
    """Yourproject development environment commands."""
    from projectkey import cd, run, run_return, runnable
    
    def runserver():
        """Run django debug web server on port 8080."""
        print "Running webserver..."
        # Run simple shell commands
        run("./venv/bin/python manage.py runserver_plus 8080 --traceback --settings=yourproject.special_settings")

    def upgrade():
        """pip upgrade on all packages and freeze to requirements afterwards."""
        # Copy and paste whole bash scripts if you like...
        run("""
            ./venv/bin/pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs ./venv/bin/pip install -U
            ./venv/bin/pip freeze > ./requirements.txt
        """)

    def smtp():
        """Run development smtp server on port 25025."""
        print "Running SMTP server..."
        run("python -m smtpd -n -c DebuggingServer localhost:25025")
    
    def striptrailingwhitespace():
        """strip the trailing whitespace from all files in your mercurial repo."""
        # Get the output of shell commands...
        repofiles = run_return("hg locate *.py").split('\n')
        
        # ...and write simple, short, python scripts to do stuff with it.
        repofiles.remove('')
        for filename in repofiles:
            with open(filename, 'r') as fh:
                new = [line.rstrip() for line in fh]
            with open(filename, 'w') as fh:
                [fh.write('%s\n' % line) for line in new]

    def inspectfile(*filenames):
        """Inspect file(s) for pylint violations."""
        # You can also change to the directory that the k command was run from, if you need that.
        cd(CWD)
        run("{0}/venv/bin/pylint --rcfile={0}/pylintrc -r n {1}".format(KEYDIR, ' '.join(filenames)))
    
    # Add this and you can run the file directly (e.g. python key.py smtp) as well as by running "k smtp".
    runnable(__name__)

Step 3: Run the 'k' command in any folder in your project::

    $ k inspectfile onefile.py twofiles.py
    [ Runs pylint on those files ]

Step 4: Add more commands.


Features
========

* Autodocuments using your docstrings.
* Use variables KEYDIR or CWD in any command to refer to key.py's directory or the directory you ran k in, inside your project.
* Passes any arguments on to the method via the command line.
* Autocomplete works out of the box.
* Comes with shortcut commands to run lists of shell commands directly, so you can copy and paste directly from existing shell scripts.
* Use the full power of python to enhance your team's development environment and automate all of the things.

For more documentation, see https://projectkey.readthedocs.org/

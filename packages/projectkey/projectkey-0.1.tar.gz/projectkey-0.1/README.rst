ProjectKey
==========

Three step process to create your project's suite of custom commands that you can invoke with one key:

Step 1: Run: "sudo pip install projectkey ; sudo activate-global-python-argcomplete"

Step 2: Create a key.py file in the root folder of your project and make it look like this::
    
    """Yourproject development environment commands."""
    from projectkey import cli, cd, run
    PROJECTNAME = "yourproject"
        
    def runserver():
        """Run django debug web server on port 8080."""
        print "Running webserver..."
        cd(KEYDIR)
        run("./venv/bin/python manage.py runserver_plus 8080 --traceback --settings=%s.dev_settings" % PROJECTNAME)

    def upgrade():
        """pip upgrade on all packages and freeze to requirements afterwards."""
        cd(KEYDIR)
        run("""
            ./venv/bin/pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs ./venv/bin/pip install -U
            ./venv/bin/pip freeze > ./requirements.txt
        """)

    def smtp():
        """Run smtp server on port 25025."""
        print "Running SMTP server..."
        run("python -m smtpd -n -c DebuggingServer localhost:25025")
    
    def striptrailingwhitespace():
        """strip the trailing whitespace from all files in your mercurial repo."""
        cd(KEYDIR)
        repofiles = run_return("hg locate *.py").split('\n')
        repofiles.remove('')
        for filename in repofiles:
            with open(filename, 'r') as fh:
                new = [line.rstrip() for line in fh]
            with open(filename, 'w') as fh:
                [fh.write('%s\n' % line) for line in new]

    def inspectfile(*filenames):
        """Inspect file(s) for pylint violations."""
        cd(CWD)
        run("{0}/venv/bin/pylint --rcfile={0}/pylintrc -r n {1}".format(KEYDIR, ' '.join(filenames)))

Step 3: Run the 'k' command in any folder in your project::

    $ k help
    Usage: k command [args]
    
    Yourproject development environment commands.
    
                    runserver - Run django debug web server on port 8000
                      upgrade - pip upgrade on all packages and freeze to requirements afterwards.
                         smtp - Run smtp server on port 25025.
      striptrailingwhitespace - strip the trailing whitespace from all files in your mercurial repo.
                  inspectfile - Inspect file(s) for pylint violations.
    
    Run 'd help [command]' to get more help on a particular command.

Step 4: Add more commands!


Features
========

* Autodocuments using your docstrings.
* Use variables KEYDIR or CWD in any command to refer to key.py's directory or the directory you ran k in - deep inside your project.
* Passes any arguments on to the method via the command line.
* Autocomplete works out of the box.
* Comes with shortcut commands to run lists of shell commands directly, so you can copy and paste directly from existing bash scripts.
* Use the full power of python to enhance your team's development environment and automate all of the things.

For more documentation, see https://projectkey.readthedocs.org/

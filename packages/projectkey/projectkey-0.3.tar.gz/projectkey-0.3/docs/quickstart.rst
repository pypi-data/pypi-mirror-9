Quickstart
==========

Step 1: Install like so: "sudo pip install projectkey ; sudo activate-global-python-argcomplete"

Step 2: Create a key.py file in the root folder of your project like this::
    
    """Yourproject development environment commands."""
    from projectkey import cd, run, run_return, runnable
    
    def runserver():
        """Run django debug web server on port 8080."""
        print "Running webserver..."
        # Change the directory to the one that you put key.py in if you need to.
        cd(KEYDIR)
        
        # Run simple shell commands
        run("./venv/bin/python manage.py runserver_plus 8080 --traceback --settings=yourproject.special_settings")

    def upgrade():
        """pip upgrade on all packages and freeze to requirements afterwards."""
        cd(KEYDIR)
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
        cd(KEYDIR)
        # Get the output of shell commands and put it in a variable
        repofiles = run_return("hg locate *.py").split('\n')
        
        # ...note that run_return prevents the output of the command it runs being printed to screen.
        
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
    [ Runs your project-customized pylint on those files ]

Step 4: Add more commands.
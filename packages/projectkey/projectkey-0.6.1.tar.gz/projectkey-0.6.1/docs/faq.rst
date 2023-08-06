FAQ
===

* What problem is this intended to solve?

It is mainly intended to cut down these types of unnecessary team interactions:

"Can you Skype me the command to run lint using our config file?"

"How do you run a test again? I keep forgetting."

"What's the exact command to run a development web server? I tried but it isn't working for me."

"You mean we actually *do* have a script to deploy docker? Where?? How do I run it?"

"Are you sure the instructions on the wiki work? They're three years old."

"Help! My git repo is broken again! I don't really understand git and I think I might have used a command wrongly."


It should also save you keystrokes for commonly run sets of commands on your own projects.


* Why do I need ProjectKey? I already have ant/fabric/nose/salt/ansible/docker/fabric

ProjectKey is not a tool intended to replace these tools.

It is a tool that is supposed to invoke all of these tools and more.



* Ok I installed it. What kind of commands do I write with it?

Anything you like, but here's the kind of commands I created with it:

* Set up [development | testing | staging | live] environments
* Run various lint tools
* Run tests
* Generate documentation
* Run builds
* Create skeleton code.
* Dump/load data from the database.
* Upgrade dependencies
* Upload or sync files.
* Tail logs on production.
* ssh into production servers.
* Run deployment scripts.
* Perform common pulling/pushing/merging/rebasing workflows.
* Common interaction tasks with docker/vagrant/ansible/puppet/etc.


* Why is the script called 'k' and not 'projectkey'?

Because you will probably be running it a lot. A one letter command means fewer
keystrokes to wear you and your keyboard out.


* Is this just for python projects?

No, you can use it on any project, you just have to create the commands in python (or translate shell commands).

You don't even really need to know python to use this. Just use the template from quickstart.


* I already have a bunch of shell scripts. Why should I use this?

Great! You can unite them in one place, and:

1) All of your project commands get united under one easy to use, discoverable, self documenting file that anybody on your team can invoke up with one key.
2) It can be run even if you are six levels deep inside of your project.
3) You can translate almost any line in your bash script to use this self.sc("your command here") so it's not hard to switch.
4) You can use a programming language that doesn't suck to write some of the more complex automation tasks.


* Shouldn't I install this in a virtualenv?

You can, but I wouldn't.

I would install it on your system python and write commands for each individual project key that understand the virtualenv that your project runs in.

It has one dependency, so it is unlikely to cause conflicts with other packages installed on your system python.
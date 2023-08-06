Why?
====

* Why do I need ProjectKey? I already have ant/fabric/nose/salt/ansible/docker

ProjectKey is not a tool intended to replace these tools. If anything, it is a tool
that is intended to invoke these tools and more.



* What problem is it intended to solve?

It is intended to cut down these types of unnecessary interactions:

"Hey buddy, can you Skype me the command to run lint using our config file?"

"How do you run a test again?"

"What's the exact command to run a development web server? I tried but it isn't working for me."

"You mean we actually *do* have a script to deploy docker? Where?? How do I run it?"

"Are you sure the instructions on the wiki work? They're three years old."

"Help! My git repo is broken again! I think I missed out the third command in the list of ones you gave me."



* What kind of commands do I write with it?

Anything you like, but here's the kind of commands I created with it:

* Set up [development | testing | staging | live] environments
* Run various lint tools
* Run tests
* Generate documentation
* Create builds
* Create skeleton code.
* Dump/load data from the database.
* Upgrade dependencies
* Tail logs on production.
* ssh into production servers.
* Run deployment scripts.
* Perform common pulling/pushing/merging/rebasing workflows.
* Common interaction tasks with docker/vagrant/ansible/puppet/etc.

FAQ
===


* Why is the script called 'k' and not 'projectkey'?

Because you will probably be running it a lot. A one letter command means fewer
keystrokes to wear you and your keyboard out.

* Is this just for python projects?

No, you can use it on any project, you just have to create the commands in python (or translate shell commands).

You don't even really need to know python to use this.

* I already have a bunch of shell scripts. What does this give me?

Great! You can unite them in one place.

1) All of your project commands get united under one easy to use, discoverable, self documenting file that anybody on your team can invoke up with one key.
2) It can be run even if you are six levels deep inside of your project.
3) You can translate almost any line in your bash script to use this self.sc("your command here") so it's not hard to switch.
4) You can use a programming language that doesn't suck to write some of the more complex automation tasks.

* Should I install ProjectKey in a virtualenv or on my system python?

I would install it on your system python and write commands for each individual project key that understand the virtualenv that your project runs in.
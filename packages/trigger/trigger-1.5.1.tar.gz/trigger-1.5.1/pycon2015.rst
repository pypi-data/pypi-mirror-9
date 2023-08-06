##########################
Trigger PyCon 2015 Sprints
##########################

Trigger loves Python! We're looking for help to make the project even easier to
use and more accessible, and trying to fix some long-standing usability issues.

Beginners are welcome, especially if you're interested in learning more about
network automation. Much of the work isn't very advanced, and may provide a
good opportunity for you to get your hands dirty in a fun library with fun
people!

We're primarily focusing on the following areas:

+ Executing commands on network devices
+ Managing authentication and credentials
+ Cleaning up and improving the documentation
+ Improving unit tests coverage across the entire project
+ Implementing for interacting with network hardware

In other words, there's no shortage of things to do!

Here is a list of the top-priority things we're looking to work on!

**Sprint Plan**

.. contents::
    :local:
    :depth: 2

Bugs
====

Commando
~~~~~~~~

Commando adapters breaks when a `LoginFailure` happens
https://github.com/trigger/trigger/issues/84

When a command returns no result, the next command may be popped and not sent
https://github.com/trigger/trigger/issues/210

Authentication & Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tacacsrc should exit gracefully when it can't read the .tacacsrc 
https://github.com/trigger/trigger/issues/78

run_cmds
~~~~~~~~

Run_cmds crashes with ReactorNotRestartable when running from device path (-p)
https://github.com/trigger/trigger/issues/152

run_cmds shouldn't hide error messages (such as command timeouts)
https://github.com/trigger/trigger/issues/177

Unable to send multiple commands with run_cmds 
https://github.com/trigger/trigger/issues/193

gong
~~~~

Add flags to `bin/gong` to force telnet or ssh connection
https://github.com/trigger/trigger/issues/36

Add SSH support for OOB in gong CLI utility
https://github.com/trigger/trigger/issues/196

Documentation
=============

Document Commando usage, examples, tutorial, etc...
https://github.com/trigger/trigger/issues/176

Document usage examples of gnng CLI utility
https://github.com/trigger/trigger/issues/190

Document usage examples of load_acl CLI utility
https://github.com/trigger/trigger/issues/191

Document bounce.py (it's not mentioned)
https://github.com/trigger/trigger/issues/174

Document TACACSRC .tackf (it's not mentioned)
https://github.com/trigger/trigger/issues/175

Document support for the Cisco ASA platform
https://github.com/trigger/trigger/issues/211

Make Trigger libraries flake8, pep8-compliant
https://github.com/trigger/trigger/issues/212

Enhancements
============

Logging
~~~~~~~

Implement log levels on Trigger debug logs, especially in twister lib
https://github.com/trigger/trigger/issues/173

Commando
~~~~~~~~

Allow Commando login timeout to be variable option
https://github.com/trigger/trigger/issues/207

Migrate device support to a driver-based plugin model
https://github.com/trigger/trigger/issues/178

Implement automated prompt answering in Commando
https://github.com/trigger/trigger/issues/91

Credentials and Authentication
------------------------------

Allow per-device passwords to be stored in .tacacsrc 
https://github.com/trigger/trigger/issues/138
  
Allow enable passwords to be stored in .tacacsrc 
https://github.com/trigger/trigger/issues/139

Allow passing of explicit credentials when connecting interactively
https://github.com/trigger/trigger/issues/160

Allow credential realms to be derived from NetDevice objects
https://github.com/trigger/trigger/issues/188

Replace shared secret for TACACSRC w/ private keys per user
https://github.com/trigger/trigger/issues/164

gnng
~~~~

`gnng` should support partial hostname lookups like `gong` does
https://github.com/trigger/trigger/issues/89

run_cmds
~~~~~~~~

Add the ability to force CLI execution in run_cmds
https://github.com/trigger/trigger/issues/153

Testing
=======

Create unit tests for interacting with hardware
https://github.com/trigger/trigger/issues/161

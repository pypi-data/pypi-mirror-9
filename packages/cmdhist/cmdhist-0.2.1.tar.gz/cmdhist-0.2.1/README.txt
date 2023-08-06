==================================
cmdhist: Never lose history again
==================================

**cmdhist** stores your commandline history **securely** in the cloud for quick and easy access anywhere.
This is how it works:

* Run **cmdhistd** daemon, signup / login to the server via commandline.
* Once logged in, the daemon would tail ~/.bash_history, and send commands as you enter them, securely via *https* to server.
* If you use multiple machines, run **cmdhistd** daemon in each one of them, logging in as yourself. It would automatically merge all the histories, so you *never lose anything*. NOTHING gets deleted from the server.
* Run **cmdhist** command to access your history. This is meant to be a replacement for the standard *history* command. Use options for advanced search.

Installation
============
cmdhist is pushed as a pip package. You can install it like so::

$ pip install cmdhist

This gives you access to two binaries::

$ cmdhistd.py  # The daemon. Must run this to signup/login and get token.
$ cmdhist.py   # The client. Run this to get/search the history.

Quick start
============
::

$ cmdhistd

Follow prompts for signup/login. Once successfully logged in, the daemon would start storing commands.

(Highly recommended) To ensure your commands get stored as soon as you enter them, set this option in your ~/.bashrc::

$ export PROMPT_COMMAND='history -a'
$ source ~/.bashrc

To query your history::

$ cmdhist  # Shows all history
$ cmdhist --binary ls  # Shows all *ls* history

Is this secure?
================

Absolutely! This is how our security works:

* All communication to server happens over https.
* Your uid and password are sent over https to the server, which returns a token. A unique 32 byte salt is generated for you at the time of sign up.
* At the client, this salt is used along with your plaintext password to generate a 256-bit key for encrypting your history using AES256 encryption. Your commands are sent to the server in encrypted form.
* This 256-bit key is never stored on the server.
* Your password is never stored on server in plaintext. We use bcrypt encryption to store it. So, there's no way for us or anyone else to read your history, without knowing your plaintext password AND 32 byte salt.

* This token gets stored in your $HOME/cmdhist directory. **Keep this token private!**
* All further communication happens over https with this token in the header.
* Server automatically resolves tokens to your account, and stores your history against it.

In short, the security is ZERO Knowledge -- inspired by SpiderOak. No one can read your history, because it gets encrypted and decrypted at client level. This also means, if you lose your password, you lose access to your history.

Things to note
===============
* There's currently no way to retrieve lost password! If you lose password, your client won't be able to access or decrypt your history. So, please ensure you remember your password!
* The setup is distributed among the client and the server. This package is the client, which runs on your machine, and is Open Sourced. The server however is not.

More about the server
======================
The server is running on Google AppEngine in the US, and is inherently scalable. For most people, this server should perform as expected. From Australia, it takes under a second to query my history, with most of the time being spent in network RTT. Yet, if you're unhappy with your performance, let me know. In fact, feel free to raise any issues or bugs, so I can fix them.

While your history is inherently secure, because its encrypted with a password that only you know, if you want to run the server within your organization, or want to keep your data within your network, you'd have to implement the server yourself. I'm surely available for guidance. Irrespective of whether I can help or not, I'm definitely interested in knowing about your use case, so shoot me a mail.

Known issues
=============
* Again: No way to retrieve lost password right now. If you lose password, you lose your history!
* I've opened up Issue Tracker in Bitbucket. So, just file your issues there.

Tested
=========
* With Python 2.7.6 on Ubuntu 14.04.1 desktop.
* Also tested on docker version 1.5.0.
* Tested on Macbook pro: Darwin Kernel Version 14.1.0. OSX Yosemite.
* Didn't test on Windows.

FAQ
=====
* My commands are not being picked up. What's going on?
The most common issue could be that you forgot to set this::

$ export PROMPT_COMMAND='history -a'
$ source ~/.bashrc

Without this, your shell has to exit before your history gets appended to ~/.bash_history, which is where cmdhistd.py picks up the commands from.
If however, this is set, then try ps aux | grep tail, and kill the tail processes. Delete the ~/cmdhist/.lock file, and re-run cmdhistd.py

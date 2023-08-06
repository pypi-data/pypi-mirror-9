#!/usr/bin/env python

import getpass
import json
import os
import requests
import signal
import subprocess
import sys
import traceback

home = os.getenv("HOME")
homedir = home + "/cmdhist"
if not os.path.exists(homedir):
    os.makedirs(homedir)
tokenfile = homedir + "/.token"
configfile = homedir + "/config.txt"
lockfile = homedir + "/.lock"

f = open(configfile)
j = json.load(f)
f.close()

if 'server' not in j:
    print "No server config found. Check " + configfile
    sys.exit()
server = j['server']

def lock():
    if os.path.exists(lockfile):
        print "Daemon already running.\nIf you're sure it's not, kill 'tail -F ~/.bash_history' and delete " + lockfile
        sys.exit()
    else:
        f = open(lockfile, 'w')

def unlock():
    print
    print 'deleting lock'
    traceback.print_stack()
    os.remove(lockfile)

def signup():
    for i in range(3):
        email = raw_input("Email: ")
        p1 = getpass.getpass()
        p2 = getpass.getpass("Repeat Password: ")
        if p1 != p2:
            print "Passwords don't match."
            continue
        d = {"email": email, "password": p1}
        r = requests.post(server+"/signup", json.dumps(d))
        if r.status_code != 200:
            r.raise_for_status()
            return

        resp = json.loads(r.text)
        if resp['Error']:
            print "Error: " + resp['Message']
            print
        else:
            print "Signed up. Please login now."
            print
            login()
            break

def login():
    # Check if token already exists.
    success = False
    for i in range(3):
        email = raw_input("Email: ")
        password = getpass.getpass()

        d = {"email": email, "password": password}
        r = requests.post(server+"/login", json.dumps(d))
        if r.status_code != 200:
            r.raise_for_status()
            return

        resp = json.loads(r.text)
        if not resp['Error']:
            f = open(tokenfile, 'w')
            f.write(resp['Message'])
            f.close()
            success = True
            break
        else:
            print "Login failed."
            print
    if not success:
        print "Failed to login. Maximum tries reached."
        sys.exit()
    else:
        print "Token stored in " + tokenfile
        store()

def login_or_signup():
        print
        ans = raw_input("Login or Signup (L/s)? ")
        if ans == "s":
            signup()
        else:
            login()

def getheaders():
    f = open(tokenfile)
    token = f.read()
    f.close()
    return {"X-Auth-Token": token}

def _store():
    f = subprocess.Popen(['tail', '-F', home+"/.bash_history"],\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = f.stdout.readline().strip()
        if len(line) == 0:
            continue
        tokens = line.split()
        binary = tokens[0]
        if tokens[0] == "sudo":
            binary = tokens[1]
        data = {"full": line, "sudo": tokens[0] == "sudo", "binary": binary}
        r = requests.post(server+"/store", json.dumps(data), headers=getheaders())

def store():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print >> sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)
    os.chdir("/")
    os.setsid()
    os.umask(0)
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print >> sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)
    _store()

def shandler(signal, frame):
    unlock()
    sys.exit()
signal.signal(signal.SIGTERM, shandler)

# Check if tokenfile exists.
try:
    lock()
    print 'cmdhist daemon: Acquired lock.'
    print
    if os.path.exists(tokenfile):
        r = requests.get(server+"/user", headers=getheaders())
        resp = json.loads(r.text)
        if resp['Error']:
            print "Invalid token."
            login_or_signup()
        else:
            print "You're logged in as: " + resp['Message']
            cont = raw_input("Continue (Y/n)? ")
            if cont != "Y" and len(cont) != 0:
                login_or_signup()
            else:
                store()
    else:
        print "No token file found."
        login_or_signup()
    unlock()
except SystemExit:
    pass
except:
    print sys.exc_info()[0]
    unlock()


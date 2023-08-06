#!/usr/bin/env python

import requests
import sys
import os
import json
import argparse

parser = argparse.ArgumentParser(description='Query commandlinst history from cloud')
parser.add_argument('-b', nargs=1, help="Only show commands for binary")

args = parser.parse_args()

home = os.getenv("HOME")
homedir = home + "/cmdhist"
if not os.path.exists(homedir):
    os.makedirs(homedir)
tokenfile = homedir + "/.token"
configfile = homedir + "/config.txt"

f = open(configfile)
j = json.load(f)
f.close()
if 'server' not in j:
    print "No server config found. Check " + configfile
    sys.exit()
server = j['server']

if not os.path.exists(tokenfile):
    print "No token file found. Please run daemon job first."
    sys.exit()

f = open(tokenfile)
token = f.read()
f.close()

data = {}
if args.b is not None and len(args.b) > 0:
    data['Binary'] = args.b[0]

r = requests.post(server+"/history", data=json.dumps(data), headers={"X-Auth-Token": token})
if r.status_code != 200:
    r.raise_for_status()
    sys.exit()

resp = json.loads(r.text)
if 'Error' in resp and resp['Error']:
    print "Error: " + resp['Message']
    sys.exit()

count = 0
for cmd in resp['Commands']:
    line = "[%d] %s%s" % (count, cmd['Full'], os.linesep)
    sys.stdout.write(line)
    count += 1
sys.stdout.flush()

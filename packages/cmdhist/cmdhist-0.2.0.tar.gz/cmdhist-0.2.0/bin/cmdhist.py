#!/usr/bin/env python

import binascii
import requests
import sys
import os
import json
import argparse

from Crypto.Cipher import AES

parser = argparse.ArgumentParser(description='Query commandlinst history from cloud')
parser.add_argument('-b', nargs=1, help="Only show commands for binary")

args = parser.parse_args()

home = os.getenv("HOME")
homedir = home + "/cmdhist"
if not os.path.exists(homedir):
    os.makedirs(homedir)
tokenfile = homedir + "/.token"
keyfile = homedir + "/.key"
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

if not os.path.exists(keyfile):
    print "No key file found. Please run daemon job first."
    sys.exit()

f = open(tokenfile)
token = f.read()
f.close()

f = open(keyfile)
ekey = f.read()
f.close()
aes = AES.new(ekey)

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
	e = binascii.unhexlify(cmd['Full'])
	line = "[%d] %s%s" % (count, aes.decrypt(e).strip(), os.linesep)
	sys.stdout.write(line)
	count += 1
sys.stdout.flush()

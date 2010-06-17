#!/usr/bin/env python

def fix_file(filename,regex,name):
    print "fixing %s..." % filename
    import re
    rx = re.compile(regex)
    old = open(filename).read()
    f = open(filename,"w")
    f.write(rx.sub(name,old))
    f.close()
    
def fix_url(filename,regex,name,url=None):
    if url is None:
        fix_file(filename,regex,"https://%s.appspot.com/"%name)
    else:
        fix_file(filename,regex,url)

name = raw_input("type an appengine name:")
email = raw_input("type an (admin) e-mail address:")
import sys
url=None
for arg in sys.argv:
    if arg.startswith("--url="):
        url=arg[6:]
fix_file("appengine/app.yaml","(?<=application: ).*",name)
fix_url("appengine/magic.py","(?<=BASE_URL=\").*(?=\")",name,url=url)
fix_url("preflight.py","(?<=BASE_URL=\").*(?=\")",name,url=url)
fix_url("sneak.py","(?<=BASE_URL=\").*(?=\")",name,url=url)
fix_file("appengine/mail.py","(?<=FROM_MAIL_ADDRESS=\").*(?=\")",email)
fix_file("appengine/mail.py","(?<=ALERT_ADMIN_ADDRESS=\").*(?=\")",email)
from getpass import getpass
print "Type a backdoor password:",
mpass = getpass()
import hashlib
fix_file("appengine/user_sn.py","(?<=elif attempt==\").*(?=\":)",hashlib.md5(mpass).hexdigest())
import os
os.system("rm -rf appengine/*.pyc")


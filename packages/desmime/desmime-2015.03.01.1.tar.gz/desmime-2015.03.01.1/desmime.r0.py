#!/usr/bin/python

import sys
import os
import subprocess
import getpass

assert len(sys.argv[1:])==1, "ERROR: usage: %s KeyFileName.pem" % sys.argv[0]
KeyFileName = sys.argv[1]
assert KeyFileName, "ERROR: KeyFileName required"
assert os.path.exists(KeyFileName), "ERROR: KeyFileName doesn't exist"

print "Please enter Key Passphrase:"
Password = getpass.getpass()
print
assert Password, "ERROR: Key Passphrase required"

print "Please enter smime message to be decrypted (headers + body), terminated by ctrl+d:"
CipherText = sys.stdin.read()
print
print
assert CipherText, "ERROR: CipherText required"

SubjectList = []
for Line in CipherText.splitlines():
	if Line[:len('subject:')].lower() == 'subject:':
		SubjectList.append(Line[len('subject:'):].strip())

if KeyFileName and Password and CipherText:
	Process = subprocess.Popen( ('openssl', 'smime', '-decrypt', '-passin', 'stdin', '-inkey', KeyFileName), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	(Out, Err) = Process.communicate('%s\n%s' % (Password, CipherText))
	if Err:
		print Err
		sys.exit(1)
	for Subject in SubjectList:
		print 'Subject: %s' % Subject
	if SubjectList:
		print
	print Out


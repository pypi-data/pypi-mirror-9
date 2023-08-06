#!/usr/bin/python

"""
Copyright (C) 2013-2014 DK

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import os
import subprocess
import getpass
import argparse

def parseArgs():
	Parser = argparse.ArgumentParser()
	Parser.add_argument('key', nargs=1, type=str, help='Recipient private key (.pem) to decrypt with')
	return Parser.parse_args()

def main():
	Args = parseArgs()
	KeyFileName = Args.key[0]
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

if __name__ == '__main__':
	main()

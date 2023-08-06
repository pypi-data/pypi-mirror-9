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
import argparse

def parseArgs():
	Parser = argparse.ArgumentParser()
	Parser.add_argument('--subject', '-s', dest='subject', type=str, help='Subject header (unencrypted)', default=None)
	Parser.add_argument('cert', nargs='+', type=str, help='Recipient certificate(s) to encrypt for')
	return Parser.parse_args()

def main():
	Args = parseArgs()
	Subject = Args.subject
	CertList = Args.cert

	for CertFileName in CertList:
		assert os.path.exists(CertFileName)

	print "Please enter plaintext to be encrypted (one or more lines), terminated by ctrl+d:"
	PlainText = sys.stdin.read()
	print
	print

	for CertFileName in CertList:
		CertName = os.path.basename(CertFileName)
		if CertName[-4:].lower()=='.pem':
			CertName=CertName[:-4]
		if CertName[-5:].lower()=='.cert':
			CertName=CertName[:-5]

		Process = subprocess.Popen( ('openssl', 'smime', '-encrypt', '-aes256', '-to', CertName, '-subject', Subject or '', CertFileName), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		(Out, Err) = Process.communicate(PlainText)
		if Err:
			print 'ERROR:'
			print Err
		else:
			print Out

if __name__ == '__main__':
	main()

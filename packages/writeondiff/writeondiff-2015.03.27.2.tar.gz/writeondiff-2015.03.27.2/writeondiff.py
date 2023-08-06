#!/usr/bin/python

"""
Copyright (C) 2015 DK

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import argparse
import os
try:
	import version
except:
	version = None

def parse_args(argv):
	parser = argparse.ArgumentParser(description="writeondiff - rewrite the file if input differ from current contents")
	if version:
		parser.add_argument('--version', action='version', version='%%(prog)s %s' % version.VERSION )
	parser.add_argument('filename', nargs=1, type=str, default=None, help='filename to handle')
	parser.add_argument('--prechange', action='append', type=str, default=[], help='command(s) to execute before writing')
	parser.add_argument('--postchange', action='append', type=str, default=[], help='command(s) to execute after writing')
	args = parser.parse_args(argv)
	return args

def main():
	args = parse_args(sys.argv[1:])
	File = open(args.filename[0],'ab+')
	File.seek(0)
	CurrentData = File.read()
	NewData = sys.stdin.read()
	if CurrentData == NewData:
		sys.exit(0)
	for Command in args.prechange:
		os.system(Command)
	File.seek(0)
	File.truncate()
	File.write(NewData)
	File.close()
	for Command in args.postchange:
		os.system(Command)
	sys.exit(1)

if __name__ == '__main__':
	main()

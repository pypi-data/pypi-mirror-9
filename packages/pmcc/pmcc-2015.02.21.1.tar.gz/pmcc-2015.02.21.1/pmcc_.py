#!/usr/bin/python

"""
Copyright (C) 2014 DK

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import os
import time
import argparse
import hashlib
import shutil
import pipes
try:
	import version
except:
	version = None

def parse_args(argv):
	parser = argparse.ArgumentParser(description="pmcc - poor man's change control")
	if version:
		parser.add_argument('--version', action='version', version='%%(prog)s %s' % version.VERSION )
	parser.add_argument('-u', '--unidiff', action='store_true', dest='unidiff', help='diff output in unidiff format')
	parser.add_argument('-b', '--ignore-space-change', action='store_true', dest='ignore_space', help='diff should ignore space mode')
	parser.add_argument('--color', action='store_true', dest='colordiff', help='use colordiff')
	parser.add_argument('-c', '--change-rev', dest='change_rev', type=int, help='revision to display the diff for')
	parser.add_argument('-f', '--from', dest='from_filename', type=int, help='filename to use as a source of snapshot')
	parser.add_argument('--di', '--diff', dest='action', action='store_const', const='di', help='display diff')
	parser.add_argument('--ci', '--commit', dest='action', action='store_const', const='ci', help='commit the current state as a new revision')
	parser.add_argument('--log', dest='action', action='store_const', const='log', help='display the list of revisions')
	parser.add_argument('--restore', dest='action', action='store_const', const='restore', help='restore the given revision')
	parser.add_argument('--cat', dest='action', action='store_const', const='cat', help='cat the given revision')
	parser.add_argument('--name', dest='action', action='store_const', const='name', help='display the filename corresponding to the given revision')
	parser.add_argument('filename', nargs='+', type=str, default=None, help='filename(s) to handle')
	args = parser.parse_args(argv)
	args.action = args.action or 'di'
	return args

def find_version_list(target_filename):
	target_dir = os.path.dirname(target_filename) or '.'
	target_nameonly = os.path.basename(target_filename)
	for sibling_nameonly in os.listdir(target_dir):
		if len(sibling_nameonly) > len(target_nameonly)+2 \
			and sibling_nameonly[:1]=='.' \
			and sibling_nameonly[1:len(target_nameonly)+1]==target_nameonly \
			and sibling_nameonly[1+len(target_nameonly)]=='.' \
			and sibling_nameonly[2+len(target_nameonly):].isdigit() \
			:
			yield os.path.join(target_dir, sibling_nameonly)

def process_target(target_filename, args):
	action_silent = args.action in ('cat', 'name')
	if not action_silent:
		print
		print '#', repr(target_filename)
	assert os.path.exists(target_filename), "ERROR: target doesn't exist: %s" % repr(target_filename)
	target_ts = int(os.path.getmtime(args.from_filename or target_filename))
	target_md5 = hashlib.md5(open(args.from_filename or target_filename,'rb').read()).hexdigest()
	snapshot_filename = os.path.join( os.path.dirname(target_filename),  '.%s.%s' % (os.path.basename(target_filename), target_ts) )
	snapshot_is_current = False
	if os.path.exists(snapshot_filename) and not action_silent:
		snapshot_md5 = hashlib.md5(open(snapshot_filename,'rb').read()).hexdigest()
		assert snapshot_md5==target_md5, "ERROR: snapshot exists but MD5 doesn't match"
		print "# OK", repr(target_filename), "<-", repr(snapshot_filename)
		snapshot_is_current = True
	if False:
		pass
	elif args.action=='ci' and (args.from_filename or not snapshot_is_current):
		print "# ci", repr(target_filename), "->", repr(snapshot_filename)
		print "cp -vp", repr(target_filename), repr(snapshot_filename)
		shutil.copy2(target_filename, snapshot_filename)
	elif args.action=='ci':
		print '# ==', repr(target_filename), '<-', repr(snapshot_filename)
	elif args.action=='di' and (args.change_rev or not snapshot_is_current):
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		if args.change_rev:
			assert args.change_rev-1 in range(len(version_list_ext))
			rev_filename = version_list_ext[args.change_rev-1]
			if args.change_rev > 1:
				last_filename = version_list_ext[args.change_rev-2]
			else:
				last_filename = '/dev/null'
		else:
			rev_filename = target_filename
			if version_list:
				last_filename = version_list[-1]
			else:
				last_filename = '/dev/null'
		print '# MM', repr(target_filename)
		if version_list:
			print '# diff', pipes.quote(last_filename), pipes.quote(rev_filename)
			sys.stdout.flush()
			diffcmd = 'diff'
			if args.colordiff:
				diffcmd = 'colordiff'
			if args.unidiff:
				diffcmd += ' -u'
			if args.ignore_space:
				diffcmd += ' -b'
			ret = os.system('%s %s %s' % (diffcmd, pipes.quote(last_filename), pipes.quote(rev_filename)))
			sys.exit(ret)
		else:
			print '# ++', repr(target_filename)
	elif args.action=='di':
		print '# ==', repr(target_filename), '<-', repr(snapshot_filename)
	elif args.action=='restore':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		assert args.change_rev and args.change_rev-1 in range(len(version_list_ext))
		rev_filename = version_list_ext[args.change_rev-1]
		print '# restore %s <= %s' % (pipes.quote(target_filename), pipes.quote(rev_filename))
		ret = os.system('cp -vp %s %s' % (pipes.quote(rev_filename), pipes.quote(target_filename)))
		sys.exit(ret)
	elif args.action=='cat':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		assert args.change_rev and args.change_rev-1 in range(len(version_list_ext))
		rev_filename = version_list_ext[args.change_rev-1]
		ret = os.system('cat %s' % pipes.quote(rev_filename))
		sys.exit(ret)
	elif args.action=='name':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		assert args.change_rev and args.change_rev-1 in range(len(version_list_ext))
		rev_filename = version_list_ext[args.change_rev-1]
		print rev_filename
		sys.exit(0)
	elif args.action=='log':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		for version_index in range(len(version_list_ext)):
			version_rev = version_index+1
			version_filename = version_list_ext[version_index]
			version_ts = int(os.path.getmtime(version_filename))
			version_tm = time.localtime(version_ts)
			version_time_str = time.strftime('%Y-%m-%d %H:%M:%S', version_tm)
			print '# [r%d] [%s] %s' % (version_rev, version_time_str, version_filename)
	else:
		raise Exception, "ERROR: unexpected action - %s" % repr(args.action)

def main():
	args = parse_args(sys.argv[1:])
	for filename in args.filename:
		process_target(target_filename=filename, args=args)

if __name__ == '__main__':
	main()

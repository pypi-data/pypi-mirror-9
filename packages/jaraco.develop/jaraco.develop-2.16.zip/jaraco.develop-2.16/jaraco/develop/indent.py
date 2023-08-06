import os
import glob
import argparse
import functools

import six
import jaraco.filesystem

no_tabs_mode = "# tab-width: 4; indent-tabs-mode: nil;"
tabs_mode = "# tab-width: 4; indent-tabs-mode: t;"

def add_mode(mode, file):
	with open(file, 'rb') as f:
		content = f.read()
	if mode in content: return
	newline = guess_newline(f)
	content = mode + newline + content
	with open(file, 'wb') as f:
		f.write(content)

def guess_newline(f):
	if isinstance(f.newlines, six.string_types):
		return f.newlines
	if isinstance(f.newlines, tuple):
		return f.newlines[0]
	return '\n'

def recursive_glob(spec):
	"""
	Take a single spec and use the first part as the root and the latter
	part as the spec.
	"""
	root, spec = os.path.split(spec)
	root = root or '.'
	return jaraco.filesystem.recursive_glob(root, spec)

def remove_tabs_mode(file):
	with open(file, 'rb') as f:
		lines = list(f)
	if not lines:
		return
	first_line = lines[0]
	if (first_line.startswith('#') and 'tab-width' in first_line
		and 'indent-tabs-mode' in first_line):
		lines = lines[1:]
	with open(file, 'wb') as f:
		f.writelines(lines)

def set_tabs_mode_cmd():
	"""
	Add an Emacs mode declaration at the beginning to declare that the file
	is using tabs or spaces.
	"""
	parser = argparse.ArgumentParser()
	add_no_tabs_mode = functools.partial(add_mode, no_tabs_mode)
	add_tabs_mode = functools.partial(add_mode, tabs_mode)
	parser.add_argument('-t', '--tabs-mode', default=add_no_tabs_mode,
		action='store_const', const=add_tabs_mode)
	parser.add_argument('-r', '--recursive', default=glob.glob, dest='glob',
		action='store_const', const=recursive_glob)
	parser.add_argument('-c', '--clear', action="store_const",
		const=remove_tabs_mode, dest='tabs_mode')
	parser.add_argument('spec', help="The file spec to change")
	args = parser.parse_args()
	file_names = args.glob(args.spec)
	map(args.tabs_mode, file_names)

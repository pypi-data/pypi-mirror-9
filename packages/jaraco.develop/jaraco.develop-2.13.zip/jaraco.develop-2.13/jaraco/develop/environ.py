#!python

from __future__ import print_function

import sys
import subprocess
import itertools

import six

from more_itertools.recipes import consume

def validate_pair(ob):
	"Return True if the object represents a pair"
	try:
		if not (len(ob) == 2):
			print("Unexpected result:", ob, file=sys.stderr)
			raise ValueError
	except:
		return False
	return True

def get_environment_from_batch_command(env_cmd, initial=None):
	"""
	Take a command (either a single command or list of arguments)
	and return the environment created after running that command.
	Note that if the command must be a batch file or .cmd file, or the
	changes to the environment will not be captured.

	If initial is supplied, it is used as the initial environment passed
	to the child process.
	"""
	if not isinstance(env_cmd, (list, tuple)):
		env_cmd = [env_cmd]
	# construct the command that will alter the environment
	env_cmd = subprocess.list2cmdline(env_cmd)
	# create a tag so we can tell in the output when the proc is done
	tag = 'Done running command'
	# construct a cmd.exe command to do accomplish this
	cmd = 'cmd.exe /s /c "{env_cmd} && echo "{tag}" && set"'.format(**vars())
	# launch the process
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=initial)
	# parse the output sent to stdout
	lines = proc.stdout
	# make sure the lines are strings
	make_str = lambda s: s.decode()
	lines = six.moves.map(make_str, lines)
	# consume whatever output occurs until the tag is reached
	consume(itertools.takewhile(lambda l: tag not in l, lines))
	# define a way to handle each KEY=VALUE line
	handle_line = lambda l: l.rstrip().split('=',1)
	# parse key/values into pairs
	pairs = map(handle_line, lines)
	# make sure the pairs are valid
	valid_pairs = filter(validate_pair, pairs)
	# construct a dictionary of the pairs
	result = dict(valid_pairs)
	# let the process finish
	proc.communicate()
	return result

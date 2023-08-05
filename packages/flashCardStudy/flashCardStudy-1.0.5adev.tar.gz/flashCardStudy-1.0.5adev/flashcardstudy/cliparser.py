import re
import errors
from sfile import get_valid_files

ARGS = [
		'-r', '--random', # 0,1
		'-s', '--stack', # 2,3
		'-n', '--new', # 4,5
		'-e', '--edit', # 6,7
		'-v', '--reverse', # 8,9
		'-w', '--wildcard', # 10,11
		'-l', '--list', # 12,13
		'-o', '--order', # 14,15
		'--author', # 16
		'-d', '--display', # 17,18
		'-a', '--all' #19,20
		] 

single_args = [ARGS[4],ARGS[5],ARGS[12], ARGS[13],
			ARGS[14],ARGS[15],ARGS[16]]

display_args = [ARGS[0], ARGS[1], ARGS[2], ARGS[3],
			ARGS[8], ARGS[9], ARGS[10], ARGS[11]]

passed_files = [] # list of files
passed_args = [] # list of args
output = [] # passes to processor

def parse(args):

	if len(args) <= 1 :
		for arg in args:
			if arg in single_args:
				break
			elif arg == ARGS[19] or arg == ARGS[20]:
				break
			elif arg not in ARGS:
				errors.id(1)
			elif arg != get_valid_files(arg):
				errors.id(1)

	for arg in args:
		if arg in ARGS:
			passed_args.append(arg)
		elif arg == get_valid_files(arg):
			passed_files.append(arg)
		elif arg != get_valid_files(arg) or arg not in ARGS:
			errors.id(1)

	check_single_arg = set(passed_args).intersection(single_args)
	# returns a list w/ elements that are both in passed_args
	# and single_args = available single_args

	if len(passed_args) > 1 and check_single_arg:
		errors.id(2)
		# you can't have more than one single_args
	elif check_single_arg and len(passed_files) > 0:
		errors.id(4)
		# you don't use files w/ single_args

	output.append(passed_files)
	output.append(passed_args)

	check_display_arg = set(passed_args).intersection(display_args)
	# returns a list w/ elements that are both in passed_args
	# and display_args = available display_args (can be multiple)
	valid_wildcard_args = [ARGS[8],[ARGS[9]],ARGS[17],
						ARGS[10],ARGS[11],ARGS[18],ARGS[19],ARGS[20]]
	# args that can be combined w/ ARGS[10/11] `wildcard`

	if len(passed_args) > 1 and ARGS[6] in passed_args or len(passed_args) > 1 and ARGS[7] in passed_args:
		errors.id(1)
		# can't use `edit` function with other args
	elif len(passed_files) > 1:
		if ARGS[6] in passed_args or ARGS[7] in passed_args: 
			errors.id(2)
			# can't use `edit` functino with more than one file
		elif ARGS[19] in passed_args or ARGS[20] in passed_args:
			errors.id(4)
			# can't use `all` with files at all
	elif len(passed_files) >= 1:
		if ARGS[19] in passed_args or ARGS[20] in passed_args:
			errors.id(4)
			# can't use `all` with files at all
		elif check_display_arg:
			# check if there are any items in display_args
			if ARGS[17] in passed_args or ARGS[18] in passed_args:
				pass
				# always need to pass `display` with other display_args
			elif ARGS[17] not in passed_args or ARGS[18] not in passed_args:
				errors.id(6)

	# checks if `wildcard` arg is properly used
	if ARGS[10] in passed_args or ARGS[11] in passed_args:
		for arg in passed_args:
			if arg not in valid_wildcard_args:
				errors.id(2)

	return output 

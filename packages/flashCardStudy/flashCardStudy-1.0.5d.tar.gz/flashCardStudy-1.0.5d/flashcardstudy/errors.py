import sys

def id(num,no_quit=None):
	
	print_help = "\nAdd `--help` or '-h' to see more."

	if num == 0:
		error = "No arguments passed."
	elif num == 1:
		error = "Invalid arguments (filename or arg)."
	elif num == 2:
		error = "You cannot use this argument in this combination."
	elif num == 3:
		error = "You must append argument to launch the program."
	elif num == 4:
		error = "Don't use this argument with file(s)."
	elif num == 5:
		error = "Invalid card ID. Try again."
	elif num == 6:
		error = "You need to add `-d`/`--display` arg"
	elif num == 7:
		error = "Can't display stack data. Stack has no cards or the file is corrupted."

	print 'Error!', error, print_help

	if no_quit:
		pass
	else:
		exit(0)

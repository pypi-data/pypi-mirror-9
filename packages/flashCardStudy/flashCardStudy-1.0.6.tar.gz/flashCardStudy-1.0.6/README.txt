==============
flashCardStudy
==============

Multi-platform command-line and GUI program for helping you study. You create your own flash cards and flip them to memorize words, definitions or whatever else you need.
You can group virtual flash cards to stacks. These stacks are actual files that hold the data. flashCardStudy thus is not database-based but file-based.
CLI part reads any stacks / stack files in current directory. These files have `.stk` extension and you can select which ones to load.
GUI part uses a default folder on your system to store the files.

Installation
============

This is a standard package written in Python 2.7. Simply clone the repo, navigate to folder where `setup.py` is and simply type (optionally put `sudo` in front of it if you're not a super user):

	python setup.py install

The package is also available on PyPi so you can install it by using [pip](https://github.com/pypa/pip).

	pip install flashCardStudy

Installation to `virtualenv` is simple too. If you do not want to install the package and just plainly use the utility, you will find the executable script in `bin/flashstudy.py`. The package contains two dependencies: PrettyTable (https://pypi.python.org/pypi/PrettyTable) and appdirs (https://pypi.python.org/pypi/appdirs). These should be installed automatically when using `pip` or `setuptools`. 

Usage
=====

The easiest way to use the program is to launch __GUI__ and go from there:

	flashstudy --gui

If you want to use command line, simply feed stack files and parameters by using `flashstudy` executable. To see all the options, you can launch help:

	flashstudy -h

Every stack has an ID, name and contains the cards. Cards must always be in stack. Stack ID defines its order, stack name defines the filename. Each stack file has `.stk` extension and is simple binary file created by Pickle (https://wiki.python.org/moin/UsingPickle) module.

Cards have their order as well which can be changed by using `-e` or `--edit` argument. You can have as many stacks containing as many cards as you want. You pass stacks (`.stk` files) as arguments plus modifier arguments. You can avoid passing filenames to utility by using `-a` or `--all` argument and combine it with modifier arguments.

Files
=====

You usually read files in command line from current directory and pass their whole names. When in GUI, the program keeps files in its own location. This location is based on operating system you're using:

__OS X:__ 
	~/Library/Application Support/flashCardStudy/flashcards/

__Linux:__
	~/.config/flashCardStudy/flashcards/

__Windows:__
	C:\Documents and Settings\<User>\Application Data\Local Settings\Ondrej Synacek\flashCardStudy\flashcards\
or
	C:\Documents and Settings\<User>\Application Data\Ondrej Synacek\flashstudy\flashcards\

You can change the default folder my editing the config file `flashcardstudy.conf` which is located in parent directory of the `flashcards/` directory from above. Change parameter `flashcards_path` in the file to do this.
You must relaunch the GUI for changes to take the effect.

Examples
========

Create new stack
----------------

	flashstudy -n

Start session
-------------

	flashstudy [filename1.stk] [filename2.stk] -d -r

This will display cards from stacks _filename1_ and _filename2_. User will be presented with cards in random fashion but stacks will keep their order. 

	flashstudy --all -v

All stacks in current directory will be used, sides of the cards will be flipped because of the `-v` (also `--reverse`) argument.
You must always use either `-d` or `-a` for session to start. You can optionally add arguments (see below).

Edit a stack
------------

	flashstudy [filename1.stk] --edit

This will launch interface for editing _filename1_ stack. You can add another cards here, as well as delete them. You can also reorder the cards if you want to have cards displayed in certain way. You can *only pass one stack file* with `-e`/`--edit` argument, you can only edit one file at a time.

Arguments
=========

`-n`  `--new`: Creates new stack file.

`-e`  `--edit`: Edit stack file.

`-l`  `--list`: List stacks and info in current directory.

`-o`  `--order`: Reorder stacks in current directory.

______


`-d`  `--display`: Will display/start session for given stack(s).

`-a`  `--all`: Will display/start session for all stacks in current directory.

`-r`  `--random`: Cards from stack are displayed randomly.

`-s`  `--stack`: Next stack will be randomly selected. 

`-v`  `--reverse`: Flips the sides of cards.

`-w`  `--wildcard`: Jumps between stacks AND cards in randomly.

______

You must provide stack file(s) for these arguments:

`-d`  `--display`

`-r`  `--random`

`-s`  `--stack`

`-v`  `--reverse`

`-w`  `--wildcard`


______

You don't provide stack file for these arguments:

`-n`  `--new`

`-e`  `--edit`

`-l`  `--list`

`-o`  `--order`

`-a`  `--all`

`-h`  `--help`

`--author`

`--gui`


When using `-e` or `--edit` argument, you can only pass single stack file.

You can substitute stack files plus `-d` or `--display` with `-a` or `--all` argument.

To be added
===========

GUI has to be tweaked a little. I want to add settings window that will allow the user to change default directory for stack files. Import/export functions will be added so you can add data from different sources (most likely CSV and XML).

import os
import ConfigParser
from appdirs import *

appauthor = "Ondrej Synacek"
appname = "flashCardStudy"
conf_file = 'flashcardstudy.conf'
separator = os.sep

def default_directory():
	return user_data_dir(appname, appauthor)

def check_conf_file():
	return os.path.exists(os.path.join(default_directory(), conf_file))

def check_datadir():
	datadir = read_conf_file(conf_file)[0]
	if not os.path.exists(datadir):
		print "data dir does not exist, creating..."
		os.makedirs(datadir, 0777)

	return datadir

def read_conf_file(conf_file):
	print "reading conf_file"
	try:
		values = []
		path_to_conf_file = os.path.join(default_directory(), conf_file) 
		print path_to_conf_file
		conf_file = ConfigParser.SafeConfigParser()
		conf_file.read(path_to_conf_file)

		for a_section in conf_file.sections():
			print "detected section: ",a_section
			for name, val in conf_file.items(a_section):
				print "reading pairs", name, val
				values.append(val)

		print "list of values: ", values
		return values

	except IOError:
		print "you don't have permission to read: ", check_conf_file()


class ConfigurationFile():

	def __init__(self):
		self.filename = conf_file
		self.defaultdir = default_directory()
		self.datadirname = 'flashcards'
		self.datadir = self.defaultdir + separator + self.datadirname + separator

	def write_datadir(self):
		configurations = ConfigParser.ConfigParser()
		configurations.add_section("user_settings")
		configurations.set("user_settings", "flashcards_path", self.datadir)
		f = open(os.path.join(self.defaultdir, self.filename), 'w+')
		configurations.write(f)
		f.close()

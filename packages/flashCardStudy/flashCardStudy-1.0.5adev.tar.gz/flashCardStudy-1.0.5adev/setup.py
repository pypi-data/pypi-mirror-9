from setuptools import setup, find_packages

setup(
    name='flashCardStudy',
    version='1.0.5a',
    author='Ondrej Synacek',
    author_email='osekdomains@gmail.com',
    packages=['flashcardstudy','tests','bin','gui'],
    scripts=['bin/flashstudy.py'],
    url='https://github.com/comatory/flashCardStudy',
    license='LICENSE.txt',
    description='multi-platform GUI and CLI based program for memorizing and studying',
    long_description=open('README.txt').read(),
	classifiers=[
				  'Programming Language :: Python',
				  'Programming Language :: Python :: 2.7',
				  'License :: OSI Approved :: MIT License',
				  'Topic :: Education',
				  ], 
	install_requires=[
		"PrettyTable","appdirs"
	],
	entry_points = {
		'console_scripts': ['flashstudy = bin.flashstudy:flashcard']
			}
)

from distutils.core import setup
from setuptools import setup, find_packages
setup(
	name = 'gooeypip',
	packages = find_packages(), # this must be the same as the name above
	version = '0.4',
	description = 'Gooey Language',
	author = 'Gooey Comps',
	author_email = 'harrise@carleton.edu',
	url = 'https://github.com/harrise/gooey-pip', # use the URL to the github repo
	download_url = 'https://github.com/harrise/gooey-pip/tarball/0.4', # I'll explain this in a second
	keywords = ['gui'], # arbitrary keywords
	classifiers = [],
)
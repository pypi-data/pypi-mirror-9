from distutils.core import setup
from setuptools import setup, find_packages
setup(
	name = 'gooeydist',
	packages = find_packages(), # this must be the same as the name above
	version = '0.1',
	description = 'Gooey Language',
	author = 'Gooey Comps',
	author_email = 'harrise@carleton.edu',
	url = 'https://github.com/GooeyComps/gooey-dist', # use the URL to the github repo
	download_url = 'https://github.com/GooeyComps/gooey-dist/tarball/0.1', # I'll explain this in a second
	keywords = ['gui'], # arbitrary keywords
	classifiers = [],
)

"""
project: asciaf (AppStudio Continuous Integration Automation Framework)


"""

# importing setuptools 
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='asciaf',
	version='1.0.0',
	description='A Python project for AppStudio CI automation',
	long_description=long_description,
	url='',
	author='Balaraj James',
	author_email='balaraj.james@metricstream.com',
	license='MIT',
	classifiers=[
		'Development Status :: 1 - Planning',
		'Intended Audience :: Developers',
		'Topic :: Office/Business :: Office Suites',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3.4',
		],

	keywords='automation appstudio process',
	packages=find_packages(),
	install_requires=[''],
	extras_require={
	},
	package_data={
		
	},
	#data_files=[('my_data', ['data/data_file'])],
	entry_points={
	},
)

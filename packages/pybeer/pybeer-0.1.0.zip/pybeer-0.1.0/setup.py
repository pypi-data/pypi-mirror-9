from distutils.core import setup

setup(
	# Application name:
	name="pybeer",

	# Version number:
	version="0.1.0",
	description="Access quality beer data through Python.",
	# Application author details:
	author="Jordan Facibene",
	author_email="jordan.facibene13@stjohns.edu",

	# Packages
	packages=["pybeer"],

	install_requires=[
		"mechanize",
	],

	license=open('LICENSE').read()
)
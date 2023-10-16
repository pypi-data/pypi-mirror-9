import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name="lyricCheck",
	version= "1.0",
	author= "Jim Boulter",
	author_email= "jboulter11@gmail.com",
	url= "jimboulter.com",
	description= "Uses pygoogle to check songs for explitives in the lyics.  Checks for the seven dirty words.",
	packages= find_packages(),
	install_requires=["pygoogle"]
	)
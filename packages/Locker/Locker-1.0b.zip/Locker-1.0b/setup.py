#!/usr/bin/env python

from distutils.core import setup

setup(
	name='Locker',
	version='1.0b',
	description='Hierarchical Resource Locking Mechanism',
	keywords='resource lock sephemore hierarchy nested',
	author='Justin Giorgi',
	author_email='justin@justingiorgi.com',
	url="https://bitbucket.org/jgiorgi/locker",
	packages=['locker'],
	install_requires=['cherrypy'],
	license="GPLv3",
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Topic :: Utilities',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
	],
)
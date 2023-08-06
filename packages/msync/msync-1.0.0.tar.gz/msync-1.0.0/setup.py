import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

from msync.version import __version__


entry_points = {}
entry_points['console_scripts'] = ['msync=msync.sync:main']

setup(	name='msync',
	version=__version__,
	description='A command line utility for one shot upload of a directory tree to dropbox.',
	author='Amol Umrale',
	author_email='babaiscool@gmail.com',
	url='http://pypi.python.org/pypi/msync/',
	packages=['msync'],
	scripts=['ez_setup.py'],
	entry_points = entry_points,
	install_requires=['dropbox'],
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 2.7'
	]
)


=====
msync
=====


Notes
=====
* Supported platforms: Linux / Python 2.7.
* Performs a one shot upload. If uploads are interrupted, they can be resumed by running command again from the same directory.
* You'll need to provide the dropbox app key and app secret. Please obtain these from here: https://www.dropbox.com/developers/apps


Usage
=====
#. To upload the directory tree under current path to dropbox root folder (under a folder with same name)::

	msync

#. Specify a different directory to upload and to a given path on dropbox::

        msync --source /home/user/data --dest backup

#. Get help::

	msync -h

Download
========
* PyPI: http://pypi.python.org/pypi/msync


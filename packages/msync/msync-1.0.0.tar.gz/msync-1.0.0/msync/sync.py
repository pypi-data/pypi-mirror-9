import dropbox
import logging
import urllib2
from time import sleep
from dropbox.rest import RESTSocketError
import sys
import os
import array
from dropbox.rest import ErrorResponse, RESTClient
import re
from urllib3.exceptions import MaxRetryError
import argparse
import signal
from os.path import expanduser, join as joinpath, exists
from os import mkdir


JOB_FILENAME = '.msync.job'
LOG_FILENAME = '.sync.log'
CONFIG_DIR = expanduser('~/.msync')
APP_KEY_FILEPATH = joinpath(CONFIG_DIR, '.key')
APP_SECRET_FILEPATH = joinpath(CONFIG_DIR, '.secret')
AT_FILEPATH = joinpath(CONFIG_DIR, '.at')

if not exists(CONFIG_DIR):
	mkdir(CONFIG_DIR)

UPLOAD_CHUNK_SIZE = 500000
CHUNKED_UPLOAD_MIN_SIZE = 1500000

PY3 = sys.version_info[0] == 3
if PY3:
    from io import StringIO
    basestring = str
else:
    from StringIO import StringIO

# globals:
file_list = None
client = None


class logger():
	logr = 0

	@staticmethod
	def getLogger():
		if (not logger.logr):
			logger.logr = logger()

		return logger.logr

	def __init__(self, print_to_stdout=True):
		self.log = logging.getLogger('sync')
		logfh = logging.FileHandler(LOG_FILENAME)
		logfh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
		self.log.addHandler(logfh)
		logst = logging.StreamHandler(sys.stdout)
		self.log.addHandler(logst)
		self.log.setLevel(logging.INFO)

		self.print_to_stdout = print_to_stdout
		return

	def info(self, msg):
		self.log.info(msg)

	def warning(self, msg):
		self.log.warning(msg)

	def error(self, msg):
		self.log.error(msg)


def authorize():
	app_key = None 
	app_secret = None

	if exists(APP_KEY_FILEPATH):
		with open(APP_KEY_FILEPATH, 'r') as f:
			app_key = f.read().strip()
	else:
		app_key = raw_input('Please enter app key: ').strip()
		with open(APP_KEY_FILEPATH, 'w') as f:
			f.write(app_key)

	if exists(APP_SECRET_FILEPATH):
		with open(APP_SECRET_FILEPATH, 'r') as f:
			app_secret = f.read().strip()
	else:
		app_secret = raw_input('Please enter app secret: ').strip()
		with open(APP_SECRET_FILEPATH, 'w') as f:
			f.write(app_secret)

	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

	authorize_url = flow.start()

	#authorize_url = flow.start()
	print '1. Go to: ' + authorize_url
	print '2. Click "Allow" (you might have to log in first)'
	print '3. Copy the authorization code.'

	code = raw_input("Enter the authorization code here: ").strip()

	access_token, user_id = flow.finish(code)

	print 'access token = ' + access_token

	with open(AT_FILEPATH, 'w') as f:
		f.write(access_token)

	return access_token


def internet_on():
    try:
        response=urllib2.urlopen('https://api.dropbox.com',timeout=5)
        return True
    except urllib2.URLError as e: pass
    return False


def upload_file(filename, dpbxpath):
	success = False

	f = 0
	try:
		f = open(filename, 'rb')
	except IOError as e:
		logger.getLogger().error(e.message)
		raise IOError

	retry_count = 0
	while not success:
		try:
			response = client.put_file(format_path(dpbxpath + filename.lstrip('.')), f)
			#logger.getLogger().info(response)
			success = True
		except Exception as e:
			logger.getLogger().error('error uploading file: ' + e.message)
			if (retry_count < 3):
				sleep(10 * pow(2, retry_count))
				retry_count += 1
				f.seek(0)
			else:
				break
		
	f.close()

	return success


def upload_chunked(filename, dpbxpath):
	success = False

	bigFile = open(filename, 'rb')
	size = os.stat(filename).st_size

	global client

	chunk_size = UPLOAD_CHUNK_SIZE
	offset = 0
	last_block = None
	upload_id = None
	max_retries = 30
	
	while offset < size:
		print '%dk ' % (offset / 1000),
		sys.stdout.flush()
		next_chunk_size = min(chunk_size, size - offset)
		if last_block == None:
			last_block = bigFile.read(next_chunk_size)
			retry_count = 0

		try:
			(offset, upload_id) = client.upload_chunk(StringIO(last_block), next_chunk_size, offset, upload_id)
			last_block = None
			if (offset == size): success = True
		except ErrorResponse as e:
			reply = e.body
			if "offset" in reply and reply['offset'] != 0:
				if reply['offset'] > offset:
					last_block = None
					offset = reply['offset']
		except Exception as e:
			logger.getLogger().error('chunk upload error: ' + e.message)
			if (retry_count < 6):
				sleep(10 * pow(2, retry_count))			
				retry_count += 1
			else:
				break
		

	bigFile.close()

	if (success):
		success = False
		path = "/commit_chunked_upload/%s%s" % (client.session.root, format_path(dpbxpath + filename.lstrip('.')))

		params = dict(
			overwrite = False,
			upload_id = upload_id
		)

		#if parent_rev is not None:
			#params['parent_rev'] = parent_rev
		retry_count = 0
		while not success:
			try:
				url, params, headers = client.request(path, params, content_server=True)
				rs = client.rest_client.POST(url, params, headers)
				#check for return code
				success = True
			except Exception as e:
				logger.getLogger().error('error committing upload: ' + e.message)
				if (retry_count < 3):
					sleep(10 * pow(2, retry_count))
					retry_count += 1
				else:
					break
					
	return success


class CommitException(Exception):
	def __init__(self):
		return


class RetryException(Exception):
	def __init(self):
		return


def format_path(path):
    """Normalize path for use with the Dropbox API.

    This function turns multiple adjacent slashes into single
    slashes, then ensures that there's a leading slash but
    not a trailing slash.
    """
    if not path:
        return path

    path = re.sub(r'/+', '/', path)

    if path == '/':
        return (u"" if isinstance(path, unicode) else "")
    else:
        return '/' + path.strip('/')


def retry_upload(filename):
	while (not internet_on()):
		sleep(15)
		logger.getLogger().info("retrying internet...")
	return upload_file(filename)


def init_client():
	access_token = None 

	if exists(AT_FILEPATH):
		with open(AT_FILEPATH, 'r') as f:
			access_token = f.read()
	else:
		access_token = authorize()

	global client
	client = dropbox.client.DropboxClient(access_token.strip())

	response = client.account_info()	
	logger.getLogger().info('Session Start :: ' + 'Name: ' + response['display_name'] + ', Email: ' + response['email'])

	return


def walk_dir_tree(dirname):
	file_list = []
	for root, dirs, files in (os.walk(dirname)):
		for f in files:
			if (not f[0] == '.'):
				file_list.append(os.path.join(root, f) + '\n')

	with open(JOB_FILENAME, 'w') as jobfile:
		jobfile.writelines(file_list)

	return

def upload_dir_tree(dirname, dpbxpath):
	resume = True
	if (not os.path.isfile(JOB_FILENAME)):
		walk_dir_tree(dirname)
		resume = False

	with open(JOB_FILENAME, 'r') as fin:
		file_list = fin.read().splitlines(True)

	total_files = len(file_list)

	if (not resume):
		if (total_files > 0):
			logger.getLogger().info("found %d files"%total_files)
		else:
			logger.getLogger().info("no files to upload")
			os.remove(JOB_FILENAME)
			return

	init_client()
	current_file = 0
	
	while (current_file < total_files):
		fn = file_list[0].strip()
		logger.getLogger().info("uploading " + str(current_file + 1) + " of " + str(total_files) + ": " + fn)

		size = os.stat(fn).st_size

		success = False
		retry_count = 0
		while not success:
			try:
				if (size <= CHUNKED_UPLOAD_MIN_SIZE):
					success = upload_file(fn, dpbxpath)
					if (not success):
						success = upload_chunked(fn, dpbxpath)
				else:
					success = upload_chunked(fn, dpbxpath)

				if success:
					logger.getLogger().info("uploaded to: " + dpbxpath)
				else:
					if (retry_count < 9):
						sleep(10 * pow(2, retry_count))
						retry_count += 1
						logger.getLogger().info("upload failed, retry# %d" % retry_count)
					else:
						raise RetryException

			except IOError:
				logger.getLogger().error("io error, skipping file..")

		del file_list[0]

		with open(JOB_FILENAME, 'w') as fout:
			fout.writelines(file_list)
		current_file += 1
		
	
	logger.getLogger().info("directory upload complete.")
	os.remove(JOB_FILENAME)

	return


def parse_arguments():
	parser = argparse.ArgumentParser('dropbox sync')
	parser.add_argument('--source', help='path to the source directory')
	parser.add_argument('--dest', help='path to target directory in your dropbox')
	args = parser.parse_args()

	dirpath = args.source if args.source else '.'
	dpbxpath = args.dest if args.dest else ''
	dpbxpath += '/' + os.path.basename(os.path.abspath(dirpath))	

	logger.getLogger().info('source dir: ' + dirpath + ', dropbox dir: ' + dpbxpath)

	return dirpath, dpbxpath


def shutdown_handler(signum = None, frame = None):
    logger.getLogger().info('system shutting down, quitting...')
    sys.exit(0)

#-- test functions -----------------------------------------------------------------------------------------------

def test_chunked_upload(filename, dpbxpath):
	init_client()
	upload_chunked(filename, dpbxpath)

def test_path_on_server(dirpath, dpbxpath):
	#init_client()
	upload_dir_tree(dirpath, dpbxpath)


#-- main program -------------------------------------------------------------------------------------------------

def main():
	try:
		signal.signal(signal.SIGTERM, shutdown_handler)
		
		(dirpath, dpbxpath) = parse_arguments()
		upload_dir_tree(dirpath, dpbxpath)
		#test_chunked_upload('./Am95U92.xcf', dpbxpath)
		#test_path_on_server(dirpath, dpbxpath)
		#init_client()
		#upload_file('./f2.png', dpbxpath)
		sys.exit(0)
	except KeyboardInterrupt:
		logger.getLogger().info(" caught keyboard interrupt, quitting...")
	except RetryException as e:
		logger.getLogger().error("maximum number of retries exceeded, quitting...")

	sys.exit(1)


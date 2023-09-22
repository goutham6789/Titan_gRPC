import logging as logger
import posixpath
import socket
import tarfile
import gzip
import zipfile
from os import listdir, makedirs, renames, remove, walk
from os.path import basename, dirname, join, isfile, getsize
from shutil import copy2, copyfileobj
from datetime import datetime
from ftplib import error_perm, FTP
from config.Executor import Executor


class FileHandler(object):  # pragma: no cover

	def __new__(cls):
		raise Exception("{} may not be instantiated.".format(cls))

	testCasePath = None

	@staticmethod
	def init_suite(outputDir, suiteName):
		Executor.set_output_dir(outputDir)
		Executor.set_suite_name(suiteName)
		Executor.set_start_datetime(datetime.now())

		suitePath = Executor.get_suite_path()
		FileHandler._create_dir_path(suitePath)

	@staticmethod
	def init_test(testName):
		Executor.set_test_name(testName)

		FileHandler.testCasePath = testPath = Executor.get_test_path()
		FileHandler._create_dir_path(testPath)

	@staticmethod
	def create_test_artifact_path(artifactPath):
		testPath = Executor.get_test_path()
		try:
			assert testPath and artifactPath
		except AssertionError:
			path = None
		else:
			path = posixpath.join(testPath, artifactPath)
			dirPath = posixpath.join(testPath, posixpath.dirname(artifactPath))
			FileHandler._create_dir_path(dirPath)
		finally:
			return path

	@staticmethod
	def _create_dir_path(dirPath):
		if dirPath and not posixpath.exists(dirPath):
			makedirs(dirPath)

	# region Private Functions
	@staticmethod
	def _write_to_file(filePath, content, mode='a'):
		"""Write parameter to the file."""
		try:
			f = open(filePath, mode)
			f.write(content.replace('\r', '')) if type(content) is str else f.write(''.join(content).replace('\r', ''))
			f.close()
		except IOError as e:
			logger.warn('Exception during file write: %s' % e)
		except TypeError as e:
			logger.warn('Maybe not set the log file path: %s. Use Initialize Test Case Path' % e)
	# endregion

	# region Path Build Funtions
	@staticmethod
	def build_case_directory():  # OBSOLETE
		"""Make new Test Case directory."""
		testPath = Executor.get_test_path()
		FileHandler._create_dir_path(testPath)
		return testPath

	@staticmethod
	def build_log_file_path(filename, subFolder=""):  # OBSOLETE
		"""Return the log file path. If 'subFolder' is filled and the folder is not exists make it."""
		if subFolder:
			path = posixpath.join(subFolder, filename)
		else:
			path = filename
		return FileHandler.create_test_artifact_path(path)

	@staticmethod
	def add_status_suffix_to_test_case(status):
		testPath = Executor.get_test_path()
		renames(testPath, "{}-{}".format(testPath, 'PASS' if status else 'FAIL'))
	# endregion

	# region File Handling
	@staticmethod
	def check_file_is_binary(filename, subFolder="", blocksize=512):
		import string

		path = FileHandler.build_log_file_path(filename, subFolder)
		s = open(path).read(blocksize)

		if "\0" in s:
			return True
		if not s:  # Empty files are considered text
			return False

		_null_trans = string.maketrans("", "")
		text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
		t = s.translate(_null_trans, text_characters)  # Get the non-text characters (maps a character to itself then use the 'remove' option to get rid of the text characters.)

		if float(len(t)) / len(s) < 0.30:  # If more than 30% non-text characters, then this is considered a binary file
			return False
		return True

	@staticmethod
	def check_file_is_hex(filename, subFolder=""):
		import string

		content = FileHandler.read_local_file(filename, subFolder).translate(None, " \n\r")
		hex_digits = set(string.hexdigits)

		return all(c in hex_digits for c in content)

	@staticmethod
	def create_binary_file_from_hex(filename, getBerLength, subFolder=""):
		import binascii

		with open(FileHandler.build_log_file_path(filename.split(".")[0] + ".1", subFolder), "wb") as file:
			hex = FileHandler.read_local_file(filename, subFolder).translate(None, "\n\r")
			origSize = len(hex.split())
			redSize = getBerLength(bytearray.fromhex(hex))
			logger.debug("Original size: {}".format(origSize))
			logger.debug("Reduced size: {}".format(redSize))

			hex = hex.split()[:redSize]
			logger.debug("New size: {}".format(len(hex)))
			hex = "".join(hex)
			file.write(binascii.unhexlify(hex))

		path = FileHandler.create_test_artifact_path(subFolder)
		return filename.split(".")[0] + ".1", posixpath.join(path, filename.split(".")[0] + ".1")

	@staticmethod
	def read_local_file(filename, subFolder="", mode="r"):
		path = FileHandler.build_log_file_path(filename, subFolder)
		with open(path, mode) as content:
			fileContent = content.read()
			if not fileContent:
				raise IOError("The input file reading result is null!")
			return fileContent

	@staticmethod
	def create_test_artifact_file(filename, content):
		path = FileHandler.build_log_file_path(filename)
		FileHandler._write_to_file(path, content, mode='w')

	@staticmethod
	def read_local_files(subFolder="", mode="r"):
		"""Return all files from directory. Use in 'for' loop or call '.next()'."""
		path = FileHandler.create_test_artifact_path(subFolder)
		for filename in listdir(path):
			if isfile(posixpath.join(path, filename)):
				yield FileHandler.read_local_file(filename, subFolder, mode), filename, posixpath.join(path, filename)

	@staticmethod
	def write_to_file(filename, content, subFolder=""):
		FileHandler._write_to_file(FileHandler.build_log_file_path(filename, subFolder), content)

	@staticmethod
	def write_cmd_to_log_file(alias, cmd, mode='a'):
		"""Write the stored time and the command to the file."""
		FileHandler._write_to_file(FileHandler.build_log_file_path("{}.log".format(alias)), '---=[TIME]=-------=[' + (datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3] + ']=').ljust(80, '-') + '\n', mode)
		FileHandler._write_to_file(FileHandler.build_log_file_path("{}.log".format(alias)), '---=[COMMAND]=----=[' + (cmd + ']=').ljust(80, '-') + '\n', mode)

	@staticmethod
	def write_response_to_log_file(alias, response, mode='a'):
		"""Write the response to the file."""
		FileHandler._write_to_file(FileHandler.build_log_file_path("{}.log".format(alias)), '---=[RESPONSE]='.ljust(100, '-') + '\n' + response + '\n\n', mode)

	@staticmethod
	def copy_file(filename, path):
		copy2(FileHandler.build_log_file_path(filename), path)

	@staticmethod
	def compress_build_file():
		zip_file = zipfile.ZipFile(FileHandler.build_log_file_path("build.zip"), 'w', zipfile.ZIP_DEFLATED)
		for root, folders, files in walk(FileHandler.testCasePath):
			for folder_name in folders:
				abspath = join(root, folder_name)
				relpath = abspath.replace(FileHandler.testCasePath, '')
				zip_file.write(abspath, relpath)
			for file_name in files:
				if file_name != 'build.zip':
					abspath = join(root, file_name)
					relpath = abspath.replace(FileHandler.testCasePath, '')
					zip_file.write(abspath, relpath)
		'''
		zf = zipfile.ZipFile(FileHandler.build_log_file_path("build.zip"), "a")
		for dirname, subdirs, files in walk(FileHandler.testCasePath):
			# for subdir in subdirs:
			# 	zf.write(join(dirname, subdir), subdir)
			for file in files:
				if file != 'build.zip':
					zf.write(join(dirname, file), file)
		zf.close()
		'''

	@staticmethod
	def unzip_file(zipFilename, delete_zip=False):
		path = zipFilename
		zf = zipfile.ZipFile(path, 'r')
		zf.extractall(FileHandler.testCasePath)
		zf.close()
		if delete_zip:
			remove(path)

	@staticmethod
	def extract_file(filePath, delete=False):
		directories, filename = filePath.rsplit('/', 1) if '/' in filePath else ('', filePath)
		tar = tarfile.open(filePath, 'r:gz')
		tar.extractall(path=directories)
		tar.close()
		if delete is True:
			remove(filePath)

	@staticmethod
	def extract_gzip_file(source_file_path, delete=False):
		directory = dirname(source_file_path)
		source_filename = basename(source_file_path)
		source_filename_parts = source_filename.split('.')
		target_filename = source_filename if len(source_filename_parts) == 1 else '.'.join(source_filename_parts[:-1])
		if len(source_filename_parts) <= 2:
			target_filename += '.DAT'
		target_file_path = join(directory, target_filename)
		with gzip.open(source_file_path, 'rb') as source_file, open(target_file_path, 'wb') as target_file:
			copyfileobj(source_file, target_file)
		if delete is True:
			remove(source_file_path)

	@staticmethod
	def check_file_exists(filename, subFolder=""):
		return posixpath.isfile(FileHandler.build_log_file_path(filename, subFolder))

	@staticmethod
	def merge_file_path(directories, filename, extension):
		filename = '{}.{}'.format(filename, extension) if extension else filename
		return '{}/{}'.format('/'.join(directories), filename) if directories else filename

	@staticmethod
	def split_file_path(filePath):
		directories, filename = filePath.rsplit('/', 1) if '/' in filePath else ('', filePath)
		directories = directories.split('/') if directories else []
		filename, extension = filename.rsplit('.', 1) if '.' in filename else (filename, '')
		return directories, filename, extension

	@staticmethod
	def split_dir_path(dirPath):
		directories, directory = dirPath.rsplit('/', 1) if '/' in dirPath else ('', dirPath)
		directories = directories.split('/') if directories else []
		return directories, directory
	# endregion

	@staticmethod
	def copy_ftp_file(ip, username, password, remote_directory, remote_file, target_file, file_extension, sub_folder=""):
		logger.warn("Deprecated! Use FtpConnection.ftp_copy instead of this!")
		try:
			# local_file_path = FileHandler.build_log_file_path(target_file, file_extension)
			# if sub_folder:
			# 	if exists(join(FileHandler.get_test_case_path(), sub_folder)) is False:
			# 		makedirs(join(FileHandler.get_test_case_path(), sub_folder))
			# 	local_file_path = join(join(FileHandler.get_test_case_path(), sub_folder), target_file + file_extension)
			# else:
			# 	local_file_path = FileHandler.build_log_file_path(target_file, file_extension)
			local_file_path = FileHandler.build_log_file_path("{}.{}".format(target_file, file_extension), sub_folder)
			remote_file = remote_file + file_extension

			logger.info('FTP copy file from ' + str(ip) + ':' + str(remote_directory) + '/' + str(remote_file) + ' to ' + str(local_file_path))

			# TODO: need to outsourced to the FTPConnection.py file

			ftp = FTP(ip)  # connect to host
			ftp.login(username, password)  # login ftp
			ftp.set_pasv(True)
			ftp.cwd(remote_directory)  # go to directory where file is located
			ftp.sendcmd("TYPE I")
			file_size = ftp.size(remote_file)
			ftp_binary_data = FtpFileSupport2(file_size, local_file_path)
			ftp.retrbinary('RETR ' + remote_file, ftp_binary_data.display_ftp_progress, blocksize=65536)  # get file
			ftp.quit()

			logger.debug('File saved to : ' + str(local_file_path))
		except (error_perm, socket.error) as e:
			logger.warn('Unable to download target file via FTP! ' + str(e))

	@staticmethod
	def upload_ftp_file(ip, username, password, remote_directory, filename, file_extension):
		logger.warn("Deprecated! Use FtpConnection.ftp_upload instead of this!")
		try:
			local_file_path = FileHandler.build_log_file_path("{}.{}".format(filename, file_extension))
			remote_file = filename + file_extension

			logger.info('FTP copy file to {}: {}/{} from {}'.format(ip, remote_directory, remote_file, local_file_path))

			# TODO: need to outsourced to the FTPConnection.py file
			ftp = FTP(ip)  # connect to host
			ftp.login(username, password)  # login ftp
			ftp.set_pasv(True)
			ftp.cwd(remote_directory)  # go to directory where file will be uploaded
			file_size = getsize(local_file_path)
			ftp_file = FtpFileSupport2(file_size)
			ftp.storbinary('STOR {}'.format(remote_file), open(local_file_path, 'rb'), callback=ftp_file.display_ftp_progress)  # upload file
			ftp.quit()

			logger.debug('File saved to : {}/{}'.format(remote_directory, remote_file))
		except (error_perm, socket.error) as e:
			logger.warn('Unable to upload target file via FTP! ' + str(e))


class FtpFileSupport2:  # pragma: no cover
	def __init__(self, file_size, local_file_path=None):
		self.file_size = file_size
		self.current_size = 0
		self.local_file_path = local_file_path
		self.progress_counter = 1

	def display_ftp_progress(self, data):
		if self.local_file_path:
			if self.current_size == 0:
				with open(self.local_file_path, 'wb') as fh:
					fh.write(data)
			else:
				with open(self.local_file_path, 'ab') as fh:
					fh.write(data)
		self.current_size += len(data)
		if self.current_size * 100 / self.file_size / 5 == self.progress_counter:
			logger.debug('{} bytes done of {} bytes: {}%'.format(self.current_size, self.file_size, self.current_size * 100 / self.file_size))
			self.progress_counter += 1

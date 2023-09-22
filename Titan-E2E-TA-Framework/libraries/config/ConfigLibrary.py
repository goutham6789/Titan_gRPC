import os
import sys

from config.Configurable import Configurable
from config.FileHandler import FileHandler
from decorators.arguments import precheck
from equipments.Equipment import Equipment

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))


class ConfigLibrary(object):
	"""Config library contain all none test case specific keywords."""
	__version__ = '2.0'
	ROBOT_LIBRARY_SCOPE = 'TEST SUITE'  # new instance created for new test suites

	# region Path
	def add_status_suffix(self, testStatus):  # pragma: no cover
		"""
		Renames the test case directory, adding 'PASS' or 'FAIL' suffix to it.
		Has to run in the teardown.

		=== Input parameter(s) ===
		| *testcaseStatus* | PASS/FAIL value of the execution verdict |
		"""
		FileHandler.add_status_suffix_to_test_case(testStatus == 'PASS')

	def compress_build_file(self):  # pragma: no cover
		"""
		Compress the result files from TC run.
		"""
		FileHandler.compress_build_file()

	def get_test_case_path(self):  # pragma: no cover
		"""
		Returns the current test case path.
		"""
		return FileHandler.testCasePath

	def initialize_test_suite_path(self, outputDir, suiteName):  # pragma: no cover
		"""Need store the LOG file path. Each Test Suite (Setup) need to start this keyword.

		=== Input parameter(s) ===
		| *outputDir* | parameter come from robot global parameter |
		| *suiteName* | parameter come from robot global parameter |
		"""
		FileHandler.init_suite(outputDir, suiteName)

	def initialize_test_case_path(self, testName):  # pragma: no cover
		"""Need store the LOG file path. Each Test Case (Setup) need to start this keyword.

		=== Input parameter(s) ===
		| *testName* | parameter come from robot global variable |
		"""
		FileHandler.init_test(testName)

	def extract_local_file(self, filePath, delete=False):
		"""
		Extract the given file.

		== Example ==
		| *Extract Local File* | FILENAME |
		| *Extract Local File* | PATH/FILENAME | ${True} |

		=== Input parameter(s) ===
		| *filePath* | Path of the file |
		| *delete* | Flag to remove the original file, False by default |
		"""
		path = FileHandler.create_test_artifact_path(filePath)
		import logging as logger
		try:
			FileHandler.extract_file(path, delete)
		except:
			try:
				logger.debug("Unable to extract file using tar, trying zip.")
				FileHandler.unzip_file(path, delete)
			except:
				logger.debug("Unable to extract file using zip, trying gzip.")
				FileHandler.extract_gzip_file(path, delete)

	def delete_local_file(self, filename):
		"""
		Delete the given file in the local directory.

		== Example ==
		| *Delete Local File* | ${filename} |

		=== Input parameter(s) ===
		| *filename* | Name of the file |
		"""
		path = FileHandler.create_test_artifact_path(filename)
		os.remove(path)

	def copy_file_from_log_dir(self, filename, toPath):
		"""
		Copy the given file to the given location.

		== Example ==
		| *Copy File From Log Dir* | FILENAME | PATH |

		=== Input parameter(s) ===
		| *equipment* | Equipment object, create in profile file |
		| *filename* | The file name |
		| *toPath* | Path of the target file |
		"""
		FileHandler.copy_file(filename, toPath)

	def generate_image_to_log(self, filename):
		"""
		Convert image file to Base64 format, and show 'info' type log in html. (Required robot api logger function to use html parameter in log.)

		== Example ==
		| *Generate Image To Log* | ${SPEACH_IMAGE} |

		=== Input parameter(s) ===
		| *filename* | Name of the file with extension. The path is the TC path. |
		"""
		import base64
		try:
			from robot.api import logger
		except ImportError:
			import logging as logger
		if isinstance(filename, list):
			for f in filename:
				logger.info('<img src="data:image/png;base64,{}" alt="{}" width="400px" height="300px"/>'.format(base64.b64encode(FileHandler.read_local_file(f, mode="rb")), filename), html=True)
		else:
			logger.info('<img src="data:image/png;base64,{}" alt="{}" width="400px" height="300px"/>'.format(base64.b64encode(FileHandler.read_local_file(filename, mode="rb")), filename), html=True)

	@staticmethod
	def get_platform():
		"""
		Returns the platform this program runs on. E.g. Linux, Windows or Java.

		== Example ==
		| *Get Platform* |

		"""
		import platform
		return platform.system()

import logging as logger
import posixpath


class Executor(object):  # pragma: no cover

	def __new__(cls):
		raise Exception("{} may not be instantiated.".format(cls))

	_output_dir = ''

	_suite_name = ''
	_test_name = ''

	_start_date = ''
	_start_time = ''

	@staticmethod
	def set_output_dir(outputDir):
		Executor._output_dir = str(outputDir).replace('\\', '/')

	@staticmethod
	def set_suite_name(suiteName):
		Executor._suite_name = str(suiteName)

	@staticmethod
	def set_test_name(testName):
		Executor._test_name = str(testName)

	@staticmethod
	def set_start_datetime(startDateTime):
		Executor._start_date = startDateTime.strftime('%Y_%m_%d')
		Executor._start_time = startDateTime.strftime('%H_%M_%S_%f')[:-3]

	@staticmethod
	def get_suite_path():
		try:
			assert Executor._output_dir and Executor._suite_name
		except AssertionError:
			logger.warn('Cannot get suite path')
			path = None
		else:
			path = posixpath.join(Executor._output_dir, Executor._suite_name)
		finally:
			return path

	@staticmethod
	def get_test_path():
		try:
			suitePath = Executor.get_suite_path()
			assert suitePath and Executor._test_name and Executor._start_date and Executor._start_time
		except AssertionError:
			logger.warn('Cannot get test path')
			path = None
		else:
			path = posixpath.join(suitePath, Executor._test_name, Executor._start_date, Executor._start_time)
		finally:
			return path

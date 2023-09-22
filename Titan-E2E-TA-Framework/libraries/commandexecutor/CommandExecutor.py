import logging as logger


class CommandExecutor(object):

	def __init__(self):
		self.prompt = '# '

		self._entered = 0
		self._result_cache = {}
		self._next_cache_cleanup = None

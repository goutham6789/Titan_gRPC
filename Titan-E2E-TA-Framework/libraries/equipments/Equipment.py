import logging as logger
from abc import ABCMeta, abstractmethod
from config.Configurable import Configurable


class Equipment(Configurable):
	"""Equipment abstract base class"""

	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, name, ip='127.0.0.1', port='80', username='', password='', loginurl = ''):
		self.name = name
		self.ip = ip
		self.port = port
		self.username = username
		self.password = password
		self.loginurl = loginurl

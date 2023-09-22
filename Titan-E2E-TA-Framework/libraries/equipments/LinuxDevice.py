import logging as logger
import re
from equipments.Equipment import Equipment
from commandexecutor.CommandExecutor import CommandExecutor


class LinuxDevice(Equipment, CommandExecutor):
	def __init__(self, name, **kwargs):
		Equipment.__init__(self, name, port='22')
		CommandExecutor.__init__(self)
		self.flag = ''
		LinuxDevice.set(self, **kwargs)

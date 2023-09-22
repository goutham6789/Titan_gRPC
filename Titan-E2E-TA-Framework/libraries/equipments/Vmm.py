import re
import logging as logger
from equipments.LinuxDevice import LinuxDevice


class Vmm(LinuxDevice):
	"""Virtual machine manager"""

	def __init__(self, name, **kwargs):
		LinuxDevice.__init__(self, name, **kwargs)
		self.prompt = '#'
		self.set(**kwargs)

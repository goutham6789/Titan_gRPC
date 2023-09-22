import logging as logger
from abc import ABCMeta
from inspect import getdoc, getmembers, ismethod


class Configurable(object):

	"""Configurable abstract base class"""

	__metaclass__ = ABCMeta

	def set(self, **kwargs):
		for key in kwargs:
			if hasattr(self, key) and not callable(getattr(self, key)):
				setattr(self, key, kwargs[key])
			else:
				raise AttributeError('Non-existing attribute: {}'.format(key))

	def help(self):
		h = '{}\n\n'.format(getdoc(self))
		h += 'Available parameters (with actual value) in {} object:\n{}\n\n'.format(self.name, '\n'.join(['  - {:<25}: {}'.format(i, j) for i, j in sorted(self.__dict__.iteritems()) if not i.startswith('_')]))
		h += 'Available properties in {} object:\n{}\n\n'.format(self.name, '\n'.join(['  - {:<25}: {}'.format(i, j) for i, j in getmembers(self) if not ismethod(j) and not i.startswith('_') and i not in ['test'] and i not in h]))
		h += 'Available functions in {} object:\n{}'.format(self.name, '\n'.join(['  - {}'.format(' '.join(map(str.capitalize, i.split('_')))) for i, j in getmembers(self) if ismethod(j) and not i.startswith('_') and i not in ['test']]))
		logger.warn(h)

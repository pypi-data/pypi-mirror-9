'''
Klarna Extension modules
'''

import sys
import os.path
import logging

if sys.version_info >= (3,):
	def clone_func(m):
		return m
else:
	def clone_func(m):
		return type(m.im_func)(m.im_func.func_code, m.im_func.func_globals)

logger = logging.getLogger('klarna.kex')

kex_path = os.environ.get('KLARNA_EX_PATH', '').split(':')

if kex_path:
	__path__ = list(map(os.path.expanduser, kex_path)) + __path__


def install(kex):
	from ..klarna import Klarna, buildversion
	if not hasattr(kex, '__kextag__'):
		raise KlarnaException("Not a valid extension class")

	tag = kex.__kextag__
	logger.info("Installing extension module %s", tag)
	for member in dir(kex):
		if not member.startswith('__'):
			m = getattr(kex, member)
			# Create a copy of the function and assign it to the same name on Klarna
			setattr(
				Klarna, member,
				clone_func(m)
			)
	Klarna._ext.add(tag)
	Klarna.VERSION = buildversion(Klarna._version, Klarna._ext)

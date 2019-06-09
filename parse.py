import inspect
import sys
import re


class Parse:
	def __init__(self, child):
		self.child = child
		self._get_description()
		self._exec()


	def _get_description(self):
		self.methods = list(filter(lambda method: not re.search('^_', method), dir(self.child)))

		self.description = dict()

		for i in range(len(self.methods)):
			self.description[self.methods[i]] = getattr(self.child, self.methods[i]).__doc__


	def _show_help(self):
		pass


	def _exec(self):
		try:
			if len(sys.argv) < 2:
				if self._greeting:
					print(self._greeting)
		except Exception:
			pass

		try:
			if sys.argv[1] == '--version':
				if self._version:
					print(self._version)
		except Exception:
			pass

		try:
			if sys.argv[1] == '--help':
				self._show_help()
		except Exception:
			pass

		try:
			func = getattr(self.child, sys.argv[1])
			params = inspect.getfullargspec(func).args
			args = sys.argv[2:]

			if len(params) == len(args):
				func(*args)
		except Exception:
			pass


def set_root(function):
	try:
		Parse._version = function()['version']
		Parse._greeting = function()['greeting']
	except KeyError as e:
		Parse._version = False
		Parse._greeting = False
		print('Error:', e)

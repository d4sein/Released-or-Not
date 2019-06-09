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
		print(f'\n{self._head}\n')
		print(f'\u001b[38;5;3mUSAGE:\u001b[0m')
		print(f'  {self._app} [arg]\n')
		print('\u001b[38;5;3mARGS:\u001b[0m')
		for k, v in self.description.items():
			full_arg = f'  -{k[0]}, --{k}'
			spacing = ' ' * (20 - len(full_arg))
			print(f'{full_arg}{spacing}{v}')
		print()


	def _exec(self):
		try:
			if len(sys.argv) < 2:
				if self._greeting:
					print(self._greeting)
		except Exception:
			pass

		try:
			if sys.argv[1] == '--version' or sys.argv[1] == '-v':
				if self._version:
					print(self._version)
		except Exception:
			pass

		try:
			if sys.argv[1] == '--help' or sys.argv[1] == '-h':
				self._show_help()
		except Exception:
			pass

		try:
			if len(sys.argv[1]) == 2:
				arg = sys.argv[1].replace('-', '')

				for k in self.description.keys():
					if k.startswith(arg):
						func = getattr(self.child, k)
						params = inspect.getfullargspec(func).args
						args = sys.argv[2:]						
				
				if len(params) == len(args):
					func(*args)
			else:
				if '--' not in sys.argv[1]:
					exit()
					
				func = getattr(self.child, sys.argv[1].replace('-', ''))
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
		Parse._head = function()['head']
		Parse._app = function()['application']
	except KeyError as e:
		Parse._version = False
		Parse._greeting = False
		print('Error:', e)

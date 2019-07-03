import inspect
import sys
import re


class Argila:
	def __init__(self, child):
		# defines child class
		self.child = child

		# I'm gathering here all the variables
		# that need to be defined before being used
		self.methods_description = {}
		self.commands = {}
		self.argv_commands = {}
		self.flags = {}
		self.hints = {}

		# executes chain of events
		self._get_description()
		self._get_command_name()
		self._get_flags()
		self._get_hints()
		self._exec()
	
	def _exec(self):
		if len(sys.argv) == 1:
			print(self._app['greeting'])

		elif sys.argv[1] == '--version' or sys.argv[1] == '-v':
			print(self._app['version'])

		elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
			if len(sys.argv) == 3:
				self._get_command_help()

			else:
				self._get_help()


		elif len(sys.argv) > 1:
			self._get_command_validation()
		
		else:
			pass

	def _get_help(self):
		print(self._app['head'])
		print('\nUSAGE:')
		print(f'\t{self._app["call"]} --help (command)')
		print('\nBUILTIN COMMANDS:')

		full_command = f'-h, --help'
		spacing = ' ' * (20 - len(full_command))
		print(f'\t{full_command}{spacing}Shows this message')

		full_command = f'-v, --version'
		spacing = ' ' * (20 - len(full_command))
		print(f'\t{full_command}{spacing}Shows version')

		print('\nCOMMANDS:')

		for command, description in zip(self.argv_commands.values(), self.methods_description.values()):
			full_command = f'{command[0]}, {command[1]}'
			# gets lenght of `full_command` so it can be
			# deducted from a fixed amount of spacing
			spacing = ' ' * (20 - len(full_command))
			print(f'\t{full_command}{spacing}{description}')

	def _get_command_help(self):
		for argv_command, command in zip(self.argv_commands.items(), self.commands.items()):

			try:
				arg_flags = self.flags[command[1]]
			except Exception:
				arg_flags = []

			try:
				opt_params = self._set_opt_params[command[1]]
			except Exception:
				opt_params = []

			try:
				metavars = self._set_metavars[command[1]]
			except Exception:
				metavars = []

			if sys.argv[2] in argv_command[1]:
				# disposable variables, don't even bother
				exec_command = getattr(self.child, command[1])
				command_args = inspect.getfullargspec(exec_command).args

				flags, positional, optional = [], [], []

				for arg in command_args:
					# if arg is in `self.flags`, with index of the current command
					if arg in arg_flags:
						# if arg is in `self._set_metavars`, with index of the current command
						if arg in metavars:
							arg = metavars[arg]
							flags.append(f'<{arg}>')
						else:
							flags.append(f'<{arg}>')

					# if arg is in `self._set_opt_params`, with index of the current command
					elif arg in opt_params:
						# if arg is in `self._set_metavars`, with index of the current command
						if arg in metavars:
							arg = metavars[arg]
							optional.append(f'[{arg}]')
						else:
							optional.append(f'[{arg}]')

					# else, it means the arg must be positional
					else:
						# if arg is in `self._set_metavars`, with index of the current command
						if arg in metavars:
							arg = metavars[arg]
							positional.append(arg)
						else:
							positional.append(arg)

				flags = ' '.join(flags)
				optional = ' '.join(optional)
				positional = ' '.join(positional)

				# this is necessary because if I printed everything
				# within one single print, in case one of the args were empty
				# it would leave an extra space between them, which is not desired
				print('USAGE:')
				
				if sum([len(positional), len(optional), len(flags)]) == 0:
					print(f'\t{self._app["call"]} {argv_command[1][1]}')
				else:
					print(f'\t{self._app["call"]} {argv_command[1][1]}', end='')

				'''This may look messy at first, but what I\'m doing is very simple.
				In order for the `positional`, `optional` and `flags` params to be
				properly spaced, it\'s necessary to know if one of them is coming after the other.
				In this regard, if there were neither `optional` nor `flags`, and I didn\'t treat it
				this way, `positional` would\'t be properly spaced from `POSITIONAL ARGS:` right below it,
				for it has the `end=""` argument, which is only necessary if there is `positional` or `flags`.'''
				if len(positional) > 0 and len(optional) > 0 or len(positional) > 0 and len(flags) > 0:
					print(f' {positional}', end='')
				elif len(positional) > 0:
					print(f' {positional}')

				if len(optional) > 0 and len(flags) > 0:
					print(f' {optional}', end='')
				elif len(optional) > 0:
					print(f' {optional}')

				if len(flags) > 0:
					print(f' {flags}')

				try:
					set_help = self._set_help[command[1]]
				except Exception:
					set_help = []

				# if positional is not empty
				if len(positional) > 0:
					print('\nPOSITIONAL ARGS:')

					for arg in command_args:

						# if there is a `set_help´ for the arg
						if arg in set_help and arg not in arg_flags and arg not in opt_params:
							if arg in metavars:
								spacing = ' ' * (20 - len(metavars[arg]))
								print(f'\t{metavars[arg]}{spacing}{set_help[arg]}')
							else:
								spacing = ' ' * (20 - len(arg))
								print(f'\t{arg}{spacing}{set_help[arg]}')

						# if not, just present the arg name
						elif arg not in set_help and arg not in arg_flags and arg not in opt_params:
							if arg in metavars:
								print(f'\t{metavars[arg]}')
							else:
								print(f'\t{arg}')

						else:
							pass

				# if optional is not empty
				if len(optional) > 0:
					print('\nOPTIONAL ARGS:')

					for arg in command_args:

						# if there is a `set_help´ for the arg
						if arg in set_help and arg in opt_params:
							if arg in metavars:
								spacing = ' ' * (20 - len(metavars[arg]))
								print(f'\t{metavars[arg]}{spacing}{set_help[arg]}')
							else:
								spacing = ' ' * (20 - len(arg))
								print(f'\t{arg}{spacing}{set_help[arg]}')
						
						# if not, just present the arg name
						elif arg not in set_help and arg in opt_params:
							if arg in metavars:
								print(f'\t{metavars[arg]}')
							else:
								print(f'\t{arg}')

						else:
							pass

				# if arg_flags is not empty
				if len(arg_flags) > 0:
					print('\nFLAGS:')

					for arg in command_args:

						# if there is a `set_help´ for the arg
						if arg in set_help and arg in arg_flags:
							if arg in metavars:
								spacing = ' ' * (20 - len(metavars[arg]))
								print(f'\t{metavars[arg]}{spacing}{set_help[arg]}')
							else:
								spacing = ' ' * (20 - len(arg))
								print(f'\t{arg}{spacing}{set_help[arg]}')

						# if not, just present the arg name
						elif arg not in set_help and arg in arg_flags:
							if arg in metavars:
								print(f'\t{metavars[arg]}')
							else:
								print(f'\t{arg}')

						else:
							pass

	def _get_command_validation(self):
		non_positional_params = []
		non_positional_args = []
		values = []
		final_args = {}

		for argv_command, command in zip(self.argv_commands.items(), self.commands.items()):

			if sys.argv[1] in argv_command[1]:
				exec_command = getattr(self.child, command[1])
				command_args = inspect.getfullargspec(exec_command).args

				try:
					arg_flags = self.flags[command[1]]
				except Exception:
					arg_flags = []

				try:
					opt_params = self._set_opt_params[command[1]]
				except Exception:
					opt_params = []

				try:
					metavars = self._set_metavars[command[1]]
				except Exception:
					metavars = {}

				for param in command_args:
					# gets all non-positional params
					if param in arg_flags or param in opt_params:
						non_positional_params.append(param)

				for arg in sys.argv[2:]:

					# checks if non-positional arg is valid
					if re.match('--\w', arg) or re.match('-\w', arg) and len(arg) == 2:
						arg = re.sub('-', '', arg)

						# ok, this is a mess, but listen:
						'''First, it checks if the arg is non-positional.
						If so, it appends to the `non_positional_args` list.'''
						if arg in non_positional_params:
							non_positional_args.append(arg)

							'''Second, if the arg is in its reduced form, it checks if
							a param in `non_positional_params` starts with it.
							If so, it appends the param to the `non_positional_args` list.'''
						elif [param for param in non_positional_params if param.startswith(arg)]:
							for param in non_positional_params:
								if param.startswith(arg):
									non_positional_args.append(param)

							'''Third, it checks if the arg is a metavar.
							If so, it gets the "original" param and
							appends it to the `non_positional_args` list.'''
						elif arg in metavars.values():
							arg = [k for k, v in metavars.items() if arg == v][0]
							non_positional_args.append(arg)

							'''Finally, if the arg is not in the `metavars` list, then it
							is in its reduced form, so it checks if any metavar in `metavars`
							starts with it. If so, it gets the "original" param from that metavar
							and appends it to the `non_positional_args` list.'''
						elif [metavar.startswith(arg) for metavar in metavars.values()]:
							for k, v in metavars.items():
								if v.startswith(arg):
									non_positional_args.append(k)

						else:
							# if there's an optional or flag arg, but doesn't
							# match any `non_positional_params`, that means
							# the command is wrong, abort!
							exit()

					else:
						values.append(arg)

				positional_params = [p for p in command_args if p not in arg_flags and p not in opt_params]
				positional = values[:len(positional_params)]
				values = values[len(positional):]

				opt_args_map = {}
				flags_map = {}

				# verifies if every optional arg has a value
				# and vice versa 
				optional = [p for p in non_positional_args if p not in arg_flags]
				if len(values) != len(optional):
					exit()

				'''It loops through everything and adds them to a dict,
				which will be used as **kwargs to call the `method`.'''
				for arg, value in zip(positional_params, positional):
					kv = {arg: value}
					final_args.update(kv)

				for arg, value in zip(non_positional_args, values):
					if arg in opt_params:
						kv = {arg: value}
						final_args.update(kv)

				for arg in non_positional_args:
					if arg in arg_flags:
						kv = {arg: True}
						final_args.update(kv)

				for arg in command_args:
					if arg not in final_args:
						kv = {arg: None}
						final_args.update(kv)

				# finally, calls the `method`.
				exec_command(**final_args)

	def _get_description(self):
		# gets child description
		self.child_description = self.child.__doc__

		# gets the methods themselves
		self.methods = list(filter(lambda method: not re.search('^_', method), dir(self.child)))
		# gets methods description
		for i in range(len(self.methods)):
			method = self.methods[i]
			description = getattr(self.child, method).__doc__
			kv = {method: description}
			self.methods_description.update(kv)

	def _get_command_name(self):
		for method in self.methods:
			try:
				# tries to get `return annotation` from method
				command = getattr(self.child, method).__annotations__['return']
				kv = {command: method}
			except KeyError:
				kv = {method: method}
				pass
			finally:
				self.commands.update(kv)
				# defines `-e` and `--example` from `command`
				a, b = f'-{command[0]}', f'--{command}'
				kv = {command: [a, b]}
				self.argv_commands.update(kv)

	def _get_flags(self):
		for method in self.methods:
			# gets attr from string `method`
			method_attr = getattr(self.child, method)
			params = inspect.signature(method_attr)

			for k, v in params.parameters.items():
				if v.default is not inspect.Parameter.empty:
					v = v.default

					try:
						kv = {k: v}
						# tries to update an existing key
						# if it can't, that means it has to create one
						self.flags[method].update(kv)
					except Exception:
						kv = {method: {k: v}}
						# updates `self.flag`
						self.flags.update(kv)

				else:
					kv = {method: ''}
					self.flags.update(kv)

	def _get_hints(self):
		for method in self.methods:
			# gets attr from string `method`
			method_attr = getattr(self.child, method)
			params = inspect.signature(method_attr)

			for k, v in params.parameters.items():
				if v.annotation is not inspect.Parameter.empty:
					v = v.annotation

					try:
						kv = {k: v}
						# tries to update an existing key
						# if it can't, that means it has to create one
						self.hints[method].update(kv)
					except KeyError:
						kv = {method: {k: v}}
						# updates `self.flag`
						self.hints.update(kv)

				else:
					kv = {method: ''}
					self.hints.update(kv)

def root(handler) -> Argila:
	# gets some general information about the program
	Argila._app = handler()

	# sets relevant variables
	# to be used by the decorators
	Argila._set_help = {}
	Argila._set_metavars = {}
	Argila._set_opt_params = {}


def set_help(dict_map) -> Argila:
	def wrapper(handler):
		method = handler.__name__
		kv = {method: dict_map}
		Argila._set_help.update(kv)

		return handler
	return wrapper


def set_metavars(dict_map) -> Argila:
	def wrapper(handler):
		method = handler.__name__
		kv = {method: dict_map}
		Argila._set_metavars.update(kv)

		return handler
	return wrapper


def set_optional_params(list_map) -> Argila:
	def wrapper(handler):
		method = handler.__name__
		kv = {method: list_map}
		Argila._set_opt_params.update(kv)

		return handler
	return wrapper


if __name__ == '__main__':
	pass

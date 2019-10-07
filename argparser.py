from sys import argv


class ArgParser:
    '''It has the methods to parse argv'''
    def __init__(self):
        # setting some general infos
        self.prefix = str() # comes before commands and args
        self.version = str() # the Application version
        self.default_message = str() # default message for when the Application is called without passing any args

        # setting the dict that will hold all commands info
        self.commands = dict()

    @staticmethod
    def config(prefix: str='--', version: str='', default_message: str='') -> None:
        '''Sets some config for Application

        Parameters:
            prefix: str
                Comes before commands and arguments
                Optional -> Defaults to: str="--"

            version: str
                The Application version
                Optional -> Defaults to: str=""

            default_message: str
                Default message to be returned when the Application is ran without passing any arguments
                Optional -> Defaults to: str=""
        '''
        parser.prefix = prefix
        parser.version = version
        parser.default_message = default_message

    @staticmethod
    async def run(app: object) -> None:
        '''Runs the Application

        Parameters:
            app: object
                Sets the Application object
         '''
        parser.app = app()

        # since the filename is also taken as an argument
        # it is necessary to deduct it from the rest of the args

        # if no arg has been passed
        if len(argv) == 1:
            print(parser.default_message)

        # if one arg has been passed
        elif len(argv) == 2:
            # and the arg is `help`
            if argv[1] == f'{parser.prefix}help':
                parser.help()

            elif argv[1] == f'{parser.prefix}version':
                print(parser.version)

                # else, looks for commands that take no args
            else:
                command = parser.exec(argv[1])
                # if one is found, call it
                if command:
                    await command

            # if more than one arg have been passed
        elif len(argv) > 2:
            # and the first arg is `help´
            if argv[1] == f'{parser.prefix}help' and argv[2] in [call for command in parser.commands for call in parser.commands[command]['calls']]:
                parser.help(argv[2])

                # else, looks for commands
            else:
                command = parser.exec(argv[1])
                # if one is found, call it
                if command:
                    await command

    @staticmethod   
    def help(call: str=None) -> None:
        '''Sends a help message

        Parameters
            call: str
                The call for a command to be matched in `parser.commands` dict
                Optional -> Defaults to: `None`
        '''
        print('Help:')

        for command in parser.commands:
            name = parser.commands[command]['name']
            
            # if `call` in available command calls
            # example: "--func" in ["--function", "--func"]
            if call in parser.commands[command]['calls']:
                calls = parser.commands[command]['calls']

                # gathers all possible positional, optional and keyword arguments from command
                try:
                    positional = [i for i in parser.commands[command]['positional'].items()]
                except KeyError:
                    positional = False

                try:    
                    optional = [(parser.prefix + k, v) for k, v in parser.commands[command]['optional'].items()]
                except KeyError:
                    optional = False

                try:
                    keyword = [(parser.prefix + k, v) for k, v in parser.commands[command]['keyword'].items()]
                except KeyError:
                    keyword = False

                print('\t{} {} {} {}\n'.format(parser.prefix + name,
                    ('(positional)' if positional else ''),
                    ('[optional]' if optional else ''),
                    ('[keyword value]' if keyword else '')))

                if len(calls) > 1:
                    aliases = ', '.join(calls[:-1])
                    print('Aliases:')
                    print(f'\t{aliases}')

                if positional:
                    print('Positional:')
                    for param in positional:
                        spacing = ' ' * (20 - len(param[0]))
                        print(f'\t{param[0]}{spacing}{param[1]}')
                
                if optional:
                    print('Optional:')
                    for param in optional:
                        spacing = ' ' * (20 - len(param[0]))
                        print(f'\t{param[0]}{spacing}{param[1]}')

                if keyword:
                    print('Keyword:')
                    for param in keyword:
                        spacing = ' ' * (20 - len(param[0]))
                        print(f'\t{param[0]}{spacing}{param[1]}')

                break
            
                # triggers the default help message for general info
            elif not call:
                description = parser.commands[command]['description']
                spacing = ' ' * (20 - len(name))

                print(f'\t{parser.prefix + name}{spacing}{description}')

    @staticmethod
    def filter_argv() -> list:
        '''Filters the argv looking for compound arguments surrounded by double quotes'''
        temp = str()
        filtered_arg = list()

        for arg in argv:
            
            if arg.startswith('"'):
                temp += arg
            
            elif arg.endswith('"'):
                temp += arg
                filtered_arg.append(temp)
                temp = str()
            
            else:
                filtered_arg.append(arg)

        return filtered_arg

    @staticmethod
    def exec(command_name: str) -> object:
        '''Parses the arguments in a dict to be passed as `kwargs` to the command's fuction

        Parameters:
            command_name: str
            The command's name to access other infos in `parser.commands` dict
        '''
        argv = parser.filter_argv()

        # returns if command is not found
        if command_name.replace(parser.prefix, '') not in parser.commands:
            return

        for command in parser.commands:
            if command_name in parser.commands[command]['calls']:
                # gets the callable command's function
                command_exec = getattr(parser.app, command)

                # if command doesn't have any params
                if len(argv) == 2:
                    return command_exec()

                params = list()

                # gathers all available positional, optional and keyword arguments
                try:
                    positional = [k for k in parser.commands[command]['positional'].keys()]
                except KeyError:
                    positional = []
                else:
                    params += positional

                try:    
                    optional = [k for k in parser.commands[command]['optional'].keys()]
                except KeyError:
                    optional = []
                else:
                    params += optional

                try:
                    keyword = [k for k in parser.commands[command]['keyword'].keys()]
                except KeyError:
                    keyword = []
                else:
                    params += keyword

                break

        args = argv[2:]
        kwargs = dict()

        # tries to match the arguments from argv with the arguments gathered from command
        for index, param in enumerate(params):
            if param in positional:
                if args[index].startswith(parser.prefix):
                    exit()
                    
                kwargs.update(
                    {
                        param: args[index]
                    }
                )

            elif param in optional and parser.prefix + param in args:
                kwargs.update(
                    {
                        param: True
                    }
                )

            elif param in keyword and parser.prefix + param in args:
                
                try:
                    value = args.index(parser.prefix + param)
                    kwargs.update(
                        {
                            param: args[value + 1]
                        }
                    )

                except IndexError:
                    pass

        return command_exec(**kwargs)


class CommandParser:
    '''Holds all command decorators'''
    @staticmethod
    def name(name: str, aliases: list=[]) -> object:
        '''Gets command name

        Parameters:
            name: str
            Command's name

            aliases: list
            Command's aliases
            Optional -> Defaults to: list=[]
        '''

        # resetting `aliases`
        aliases = [] if not aliases else aliases

        calls = aliases
        calls.append(name)

        calls = [parser.prefix + call for call in calls]

        def wrapper(function: object) -> object:
            description = function.__doc__ if function.__doc__ else ''

            parser.commands[function.__name__] = {
                'name': name,
                'description': description,
                'calls': calls
            }

            return function

        return wrapper

    @staticmethod
    def positional(positional: dict) -> object:
        '''Gets command positional parameters

        Parameters:
            positional: dict
            Command's positional parameters and their description
        '''
        def wrapper(function: object) -> object:
            parser.commands[function.__name__].update(
                {
                    'positional': positional
                }
            )

            return function

        return wrapper

    @staticmethod
    def optional(optional: dict) -> object:
        '''Gets command optional parameters

        Parameters:
            optional: dict
            Command's optional parameters and their description
        '''
        def wrapper(function: object) -> object:
            parser.commands[function.__name__].update(
                {
                    'optional': optional
                }
            )

            return function

        return wrapper

    @staticmethod
    def keyword(keyword: dict) -> object:
        '''Gets command keyword parameters

        Parameters:
            keyword: dict
            Command's keyword parameters and their description
        '''
        def wrapper(function: object) -> object:
            parser.commands[function.__name__].update(
                {
                    'keyword': keyword
                }
            )

            return function

        return wrapper


parser = ArgParser()
command = CommandParser()
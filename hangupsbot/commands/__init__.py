from hangups.conversation import Conversation
import hangupsbot
from hangupsbot.utils import text_to_segments
from copy import deepcopy
import os, glob, asyncio
import threading, time

class CommandDispatcher:
    """Register commands and run them"""
    def __init__(self):
        self.commands = {}
        self.commands_admin = []
        self.unknown_command = None

    def get_admin_commands(self, bot, conv_id):
        """Get list of admin-only commands (set by plugins or in config.json)"""
        commands_admin = bot.get_config_suboption(conv_id, 'commands_admin') or []
        return list(set(commands_admin + self.commands_admin))

    def __scorecommands(self, commandname, keyword=None):
        print("Command Received: " + str(commandname) + ", Keyword Received: " + str(keyword))

        __commandName = commandname
        __highestScore = 0

        if keyword == None: keyword = []
        keyword.append(commandname)
        keyword = set(keyword)

        for func_name in self.commands:
            func_keyword = []
            #print(func_name + " Tags: " + str(self.commands[func_name][1]))
            func_keyword = deepcopy(self.commands[func_name][1])
            func_keyword.append(func_name)
            #print(func_name + " After append: " + str(func_keyword))
            func_keyword = set(func_keyword)
            
            # commandName is same with func_name: +2
            # func_name is in the command_keyword: +1
            # commandName is in the func_keyword: +1
            # func_keyword intersect command_keyword: +1
            __commandScore = 0
            if commandname == func_name: __commandScore = __commandScore + 1
            
            #print("Comparing: " + str(keyword) + " with " + str(func_keyword))
            for kw in list(keyword & func_keyword):
            # since the commandname and the funcname is added to keyword list if it is the
            # same it actualy add +2 because the statement above.
                __commandScore =  __commandScore + 1

            #print(func_name + " Score: " +str(__commandScore))

            if __highestScore < __commandScore:
                __commandName = func_name
                __highestScore = __commandScore

        print("Highest Score: " + str(__commandName))
        return __commandName

    @asyncio.coroutine
    def run(self, bot, event, keyword=None, *args, **kwds):
        """Run command
           since the command now has a keyword we need to do a scoring
           run the command with the highest score.
           1. loop all commands 
           2. calculate all score
           3. run highest score.
           4. the parameter ?
        """
        if keyword == None: keyword = []

        try:
            #func = self.commands[args[0]][0]
            #func_keyword = self.commands[args[0]][1]   
            func_name = self.__scorecommands(args[0],keyword)      
            func = self.commands[func_name][0]
            #print(str(func))
        except KeyError:
            if self.unknown_command:
                func = self.unknown_command
            else:
                raise

        args = list(args[1:])
        #print("Arguments: " + str(args))

        try:
            yield from func(bot, event, *args, **kwds)
        except Exception as e:
            print(e)
      
    def register(self, *args, admin=False, keyword=[]):
        """Decorator for registering command
           added keyword array of the command keyword.
        """
        def wrapper(func):
            # Automatically wrap command function in coroutine
            func = asyncio.coroutine(func)
            if keyword == None: keyword [func.__name__]
            #print("Registering: " + func.__name__ + " Key: " + str(keyword))
            self.commands[func.__name__] = [func,keyword]
            if admin:
                self.commands_admin.append(func.__name__)
            return func

        # If there is one (and only one) positional argument and this argument is callable,
        # assume it is the decorator (without any optional keyword arguments)
        if len(args) == 1 and callable(args[0]):
            return wrapper(args[0])
        else:
            return wrapper

    def register_unknown(self, func):
        """Decorator for registering unknown command"""
        # Automatically wrap command function in coroutine
        func = asyncio.coroutine(func)
        self.unknown_command = func
        return func


# Create CommandDispatcher singleton
command = CommandDispatcher()

# Build list of commands
_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

# Load all commands
from hangupsbot.commands import *

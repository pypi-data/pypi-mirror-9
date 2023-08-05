"""
.. module:: shell
   :platform: Unix
      :synopsis: This module contains the shell functionality of clnews.

      .. moduleauthor:: Alexandros Ntavelos <a.ntavelos@gmail.com>

      """
import sys
from subprocess import Popen, PIPE
import errno

from colorama import init as colorama_init, Fore, Back, Style
import readline
from news import Event, Channel
from exception import ChannelRetrieveEventsError, ShellCommandDoesNotExist, \
ShellCommandChannelNotFound, ShellCommandExecutionError, ShellCommandOutputError
import config

reload(sys)
sys.setdefaultencoding("utf-8")

COMMANDS = {
    '.help': ('.help', 'show this help message and exit'),
    '.list': ('.list', 'lists all the available channels'),
    '.get': ('.get', 'retrieves the news of a given channel, e.g.: .get cnn'),
    '.quit': ('.quit', 'exits the application.')
}


def less(func):
    """Less decorator.

    Pipes the output of the decorated function into the less commans
    
    """
    def inner(self):
        p = Popen(['less', '-R'], stdin=PIPE)
        line = func(self)
        try:
            p.stdin.write(line)
        except IOError as e:
            if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
                # Stop loop on "Invalid pipe" or "Invalid argument".
                # No sense in continuing with broken pipe.
                return
            else:
                # Raise any other error.
                raise

        p.stdin.close()
        p.wait()
    return inner


class Command(object):
    """ Abstract class implementing the shell commands.

    It implements the basic functionality of the shell commands and serves as a
    parent class.    
    """
    def __init__(self, name, description):
        """Initializes of the command.

        Args:
            name (str): The actual name of the command
            description (str): The description of the command
        """
        self.name = name
        self.description = description
        # saves the output of the command
        self.buffer = None

    def execute(self):
        pass

    def print_output(self):
        pass


class CommandHelp(Command):
    """ Implements the .help command. 
    
    Derives from :class:`shell.Command` class and implements the .help command 
    """
    def __init__(self):
        """Initializes the class."""
        name, description = COMMANDS['.help']
        super(CommandHelp, self).__init__(name, description)

    def execute(self):
        """ Executes the command.
        
        Puts in the buffer the output of the command
        """

        self.buffer = "CLNews %s \n\n" % config.VERSION
        self.buffer += "Options:\n"

        for _, (name, description) in COMMANDS.iteritems():
            self.buffer += "\t%10s\t%s\n" % (name, description) 
        self.buffer += "\n"

    def print_output(self):
        """ Prints the output of the command"""
        print self.buffer


class CommandList(Command):
    """ Implements the .list command. 
    
    Derives from :class:`shell.Command` class and implements the .list command 
    """

    def __init__(self):
        """ Initializes the class."""
        name, description = COMMANDS['.list']
        super(CommandList, self).__init__(name, description)

    def execute(self):
        ''' Executes the command.

        Lists all the available channels.
        '''
        self.buffer = [(key, data["name"]) 
                       for key, data 
                       in config.CHANNELS.iteritems()]
    
    @less
    def print_output(self):
        """ Prints the output of the command
        
        Raises:
            ShellCommandOutputError: An error occured when the buffer is not a 
            list.
        """
        try:
            output = ["%s| Name %s| Code" % (5 * " ", 15 * " "),
                      "%s+%s+%s" % (5 * "-", 21 * "-", 20 * "-")]
            output += ["%5s|%20s | %s" % (str(i + 1), name, short)
                       for i, (short, name) 
                       in enumerate(self.buffer)]

            return "\n".join(output)
        except TypeError:
            # the buffer is not a list as expected
            raise ShellCommandOutputError


class CommandGet(Command):
    """ Implements the .get command. 
    
    Derives from :class:`shell.Command` class and implements the .get command 
    """

    def __init__(self, channel_name, channel_url):
        """ Initializes the class
        
        Args:
            channel_name (str): The name of the channel
            channel_url (str): The URL of the channel feed
        """
        
        name, description = COMMANDS['.get']
        super(CommandGet, self).__init__(name, description)
        self.channel_name = channel_name
        self.channel_url = channel_url

    def execute(self):
        """ Executes the command.

        Retrieves the events for the given channel.

        Raises:
            ShellCommandExecutionError: An error occured when the event
            retrieval fails.
        """
        chan = Channel(self.channel_name, self.channel_url)

        try:
            self.buffer = chan.get_events()
        except ChannelRetrieveEventsError:
            raise ShellCommandOutputError

    @less
    def print_output(self):
        """ Prints the output of the command

        Raises:
            ShellCommandOutputError: An error occured when the buffer is not a
            list.
        """
        try:
            output = ["%3s. %s, %s\n     %s\n     %s\n" % \
                      (Fore.WHITE + Style.BRIGHT + str(i + 1), event.title,
                      Fore.MAGENTA + event.date,
                      Fore.WHITE + Style.DIM + event.url,
                      Fore.YELLOW + Style.NORMAL + event.summary)
                      for i, event
                      in enumerate(self.buffer)]

            return "\n".join(output)

        except TypeError:
            # the buffer is not a list as expected
            raise ShellCommandOutputError


class Shell(object):
    """ Implements the shell functionality."""

    def __init__(self):
        """ Initializes the class."""
        self.command = None
        colorama_init()
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')

    def _prompt(self, text):
        sys.stdin.flush()
        return raw_input(text)

    def _analyse_input(self, user_input):
        if '.quit' == user_input:
            raise EOFError

        tokens = user_input.split()
        first = tokens[0]

        if first not in COMMANDS.keys():
            raise ShellCommandDoesNotExist

        if first == '.help':
            self.command = CommandHelp()

        if first == '.list':
            self.command = CommandList()

        if first == '.get':
            if len(tokens) < 2:
                raise ShellCommandChannelNotFound

            if tokens[1] not in config.CHANNELS.keys():
                raise ShellCommandChannelNotFound

            channel = config.CHANNELS[tokens[1]]
            self.command = CommandGet(channel['name'], channel['url'])

        return self.command

    def run(self):
        """ Runs infinitely executing the commands given in input."""

        print "CLNews %s \n" % config.VERSION
        command = Command('name', 'description')
        while True:
            try:
                user_input = self._prompt("news> ")
                if user_input:
                    command = self._analyse_input(user_input)
            except (EOFError, KeyboardInterrupt):
                print
                break
            except ShellCommandDoesNotExist, exc:
                print str(exc), 'Use .help to see the available options'
                continue
            except ShellCommandChannelNotFound:
                print('The channel was not found. '
                       'Use .list to see the available ones.')
                continue

            try:
                command.execute()
                command.print_output()
            except ShellCommandExecutionError:
                print "An error occured while executing the command."
                continue
            except ShellCommandOutputError:
                print "An error occured while printing the resultof the command"
                continue

def main():
    shell = Shell()
    shell.run()

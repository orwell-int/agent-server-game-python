"""Agent that is used to communicate with server game."""

import logging
import sys
import socket

from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager
import cliff.interactive
import cmd2

import zmq


class RegisteredCommand(Command):

    """Parent class used to easily register commands."""

    @classmethod
    def register_to(klass, command_manager):
        """Simple wrapper around #add_command."""
        command_manager.add_command(klass._command_name, klass)


class SingleCommand(RegisteredCommand):

    """Command that does not expect a reply but only a status that
    is ignored.
    """

    def take_action(self, parsed_args):
        """Send the command and ignore the reply."""
        things = []
        for thing in parsed_args.object:
            if ' ' in thing:
                thing = '"%s"' % thing
            things.append(thing)
        joined = ' '.join(things)
        reply = self.app.send_and_receive(
            self._command_name + ' %s' % joined)
        self.log.debug('discard reply: ' + str(reply))


class SetAnonymous(SingleCommand):

    """Set the property of an object."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """Override the parser to add custom arguments."""
        parser = super(SetAnonymous, self).get_parser(prog_name)
        parser.add_argument(
            'property',
            choices=self._properties)
        parser.add_argument(
            'value')
        return parser

    def take_action(self, parsed_args):
        """Send the command and ignore the reply."""
        self.app.send_and_receive(
            ' '.join((
                self._command_name,
                parsed_args.property,
                parsed_args.value)))


class SetGame(SetAnonymous):
    "Set the property of the game."

    log = logging.getLogger(__name__)

    _command_name = 'set game'
    _properties = ['duration', ]


class Set(SingleCommand):

    """Set the property of an object."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """Override the parser to add custom arguments."""
        parser = super(Set, self).get_parser(prog_name)
        parser.add_argument(
            'name')
        parser.add_argument(
            'property',
            choices=self._properties)
        parser.add_argument(
            'value')
        return parser

    def take_action(self, parsed_args):
        """Send the command and ignore the reply."""
        if ' ' in parsed_args.name:
            name = '"%s"' % parsed_args.name
        else:
            name = parsed_args.name
        self.app.send_and_receive(
            ' '.join((
                self._command_name,
                name,
                parsed_args.property,
                parsed_args.value)))


class SetRobot(Set):
    "Set the property of a robot."

    log = logging.getLogger(__name__)

    _command_name = 'set robot'
    _properties = ['video_url', ]


class SetTeam(Set):
    "Set the property of a team."

    log = logging.getLogger(__name__)

    _command_name = 'set team'
    _properties = ['score', ]


class Get(SingleCommand):

    """Get the property of an object."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """Override the parser to add custom arguments."""
        parser = super(Get, self).get_parser(prog_name)
        parser.add_argument(
            'name')
        parser.add_argument(
            'property',
            choices=self._properties)
        return parser

    def take_action(self, parsed_args):
        """Send the command and display the reply."""
        if ' ' in parsed_args.name:
            name = '"%s"' % parsed_args.name
        else:
            name = parsed_args.name
        message = self.app.send_and_receive(
            ' '.join((
                self._command_name,
                name,
                parsed_args.property)))
        # it is not nice but this test prevent printing the mocks in tests
        if isinstance(message, str):
            self.log.info(message)


class GetRobot(Get):
    "Get the property of a robot."

    log = logging.getLogger(__name__)

    _command_name = 'get robot'
    _properties = ['video_url', ]


class GetGame(SingleCommand):

    """Get the property of the game."""

    log = logging.getLogger(__name__)

    _command_name = 'get game'
    _properties = ['time', 'duration', ]

    def get_parser(self, prog_name):
        """Override the parser to add custom arguments."""
        parser = super(GetGame, self).get_parser(prog_name)
        parser.add_argument(
            'property',
            choices=self._properties)
        return parser

    def take_action(self, parsed_args):
        """Send the command and display the reply."""
        message = self.app.send_and_receive(
            ' '.join((
                self._command_name,
                parsed_args.property)))
        # it is not nice but this test prevent printing the mocks in tests
        if isinstance(message, str):
            self.log.info(message)


class List(SingleCommand):

    """List something."""

    log = logging.getLogger(__name__)
    port = None
    host = socket.gethostbyname(socket.getfqdn())

    def take_action(self, parsed_args):
        """Send the list command."""
        message = self.app.send_and_receive(self._command_name)
        # it is not nice but this test prevent printing the mocks in tests
        if isinstance(message, str):
            self.log.info(message)


class ListPlayer(List):

    """List all players."""

    log = logging.getLogger(__name__)
    _command_name = 'list player'


class ListRobot(List):

    """List all robots."""

    log = logging.getLogger(__name__)
    _command_name = 'list robot'


class ListTeam(List):

    """List all teams."""

    log = logging.getLogger(__name__)
    _command_name = 'list team'


class ListFlag(List):

    """List all flags."""

    log = logging.getLogger(__name__)
    _command_name = 'list flag'


class Add(SingleCommand):

    """Add something."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """Override the parser to add custom argument."""
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
        return parser


class AddPlayer(Add):

    """Add a player."""

    log = logging.getLogger(__name__)
    _command_name = 'add player'


class AddRobot(Add):

    """Add a robot."""

    log = logging.getLogger(__name__)
    _command_name = 'add robot'


class AddTeam(Add):

    """Add a team."""

    log = logging.getLogger(__name__)
    _command_name = 'add team'


class Remove(SingleCommand):

    """Remove something."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        """Override the parser to add custom argument."""
        parser = super(Remove, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
        return parser


class RemovePlayer(Remove):

    """Remove a player."""

    log = logging.getLogger(__name__)
    _command_name = 'remove player'


class RemoveRobot(Remove):

    """Remove a robot."""

    log = logging.getLogger(__name__)
    _command_name = 'remove robot'


class RemoveTeam(Remove):

    """Remove a team."""

    log = logging.getLogger(__name__)
    _command_name = 'remove team'


class Start(SingleCommand):

    """Start something."""

    log = logging.getLogger(__name__)
    _command_name = 'start'

    def get_parser(self, prog_name):
        """Override the parser to add custom argument."""
        parser = super(Start, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1,
            choices=('game',))
        return parser


class Stop(SingleCommand):

    """Stop something."""

    log = logging.getLogger(__name__)
    _command_name = 'stop'

    def get_parser(self, prog_name):
        """Override the parser to add custom argument."""
        parser = super(Stop, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1,
            choices=('application', 'game'))
        return parser


class RegisterRobot(SingleCommand):

    """Register a robot."""

    log = logging.getLogger(__name__)
    _command_name = 'register robot'

    def get_parser(self, prog_name):
        """Override the parser to add custom argument."""
        parser = super(RegisterRobot, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
        return parser


class UnregisterRobot(SingleCommand):

    """Unregister a robot."""

    log = logging.getLogger(__name__)
    _command_name = 'unregister robot'

    def get_parser(self, prog_name):
        """Override the parser to add custom argument."""
        parser = super(UnregisterRobot, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
        return parser


class InteractiveApp(cliff.interactive.InteractiveApp):
    def __init__(self, *args, **kwargs):
        super(InteractiveApp, self).__init__(*args, **kwargs)

    def default(self, line):
        # try to replace the "wrong" behaviour of cliff::InteractiveApp::default
        line_parts = self._split_line(line)
        if isinstance(line, cmd2.Statement):
            line_parts = [line_parts[0]] + line.arg_list
        ret = self.parent_app.run_subcommand(line_parts)
        if self.errexit:
            # Only provide this if errexit is enabled,
            # otherise keep old behaviour
            return ret


class AgentApp(App):

    """Click application.

    This is the class the calls the different commands and has all the
    zmq objects.
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        """Call parent constructor and register the commands."""
        command_manager = CommandManager('orwell.agent')
        super(AgentApp, self).__init__(
            description='Orwell agent.',
            version='0.0.1',
            command_manager=command_manager,
            interactive_app_factory=InteractiveApp,
            )
        Start.register_to(command_manager)
        Stop.register_to(command_manager)
        ListPlayer.register_to(command_manager)
        ListRobot.register_to(command_manager)
        ListTeam.register_to(command_manager)
        ListFlag.register_to(command_manager)
        AddPlayer.register_to(command_manager)
        AddRobot.register_to(command_manager)
        AddTeam.register_to(command_manager)
        RemovePlayer.register_to(command_manager)
        RemoveRobot.register_to(command_manager)
        RemoveTeam.register_to(command_manager)
        RegisterRobot.register_to(command_manager)
        UnregisterRobot.register_to(command_manager)
        SetGame.register_to(command_manager)
        SetRobot.register_to(command_manager)
        SetTeam.register_to(command_manager)
        GetRobot.register_to(command_manager)
        GetGame.register_to(command_manager)
        self._zmq_context = None
        self._zmq_req_socket = None

    def build_option_parser(
            self,
            description,
            version,
            argparse_kwargs=None):
        """Build the parser."""
        parser = super(AgentApp, self).build_option_parser(
            description,
            version,
            argparse_kwargs)
        parser.add_argument(
            '-p',
            '--port',
            type=int,
            default=9003,
            help='The port to send commands to.')
        parser.add_argument(
            '-a',
            '--address',
            type=str,
            default='127.0.0.1',
            help='The address to send commands to.')
        return parser

    def initialize_app(self, argv):
        """Create the zmq objects."""
        self.log.debug('initialize_app ; argv = ' + str(argv))
        self._zmq_context = zmq.Context()
        self.log.debug('created context = %s' % self._zmq_context)
        self._zmq_req_socket = self._zmq_context.socket(zmq.REQ)
        connection_string = "tcp://%s:%i" % (
            self.options.address,
            self.options.port)
        self.log.debug('created push socket | %s' % connection_string)
        self._zmq_req_socket.setsockopt(zmq.LINGER, 1)
        self._zmq_req_socket.connect(connection_string)
        self.log.debug('after push socket connect')
        # # if we do not wait the first messages are lost
        # import time
        # time.sleep(0.0001)
        # or maybe it is not lost after all

    def send_and_receive(self, command):
        """Send a command and block until the response is received."""
        self.log.debug('send command "%s"' % command)
        self.log.debug('call socket.send("%s")' % command)
        send_result = self._zmq_req_socket.send_string(command)
        self.log.debug('send -> ' + str(send_result))
        self.log.debug('try to receive a message')
        message = self._zmq_req_socket.recv_string()
        self.log.debug('received: %s', message)
        return message

    def prepare_to_run_command(self, cmd):
        """Debug output."""
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        """Debug output."""
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    """Entry point for the tests and program."""
    myapp = AgentApp()
    return myapp.run(argv)


if "__main__" == __name__:
    sys.exit(main(sys.argv[1:]))  # pragma: no coverage

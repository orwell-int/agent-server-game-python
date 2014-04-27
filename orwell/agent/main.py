import logging
import sys

from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager


class RegisteredCommand(Command):
    def __init__(self, app, app_args):
        super(RegisteredCommand, self).__init__(app, app_args)

    @classmethod
    def register_to(klass, command_manager):
        command_manager.add_command(klass._command_name, klass)


class SingleCommand(RegisteredCommand):
    def take_action(self, parsed_args):
        self.app.send(self._command_name + ' ' + parsed_args.object[0])


class Add(SingleCommand):
    "Add something."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
        return parser


class AddPlayer(Add):
    "Add a player."

    log = logging.getLogger(__name__)
    _command_name = 'add player'


class AddRobot(Add):
    "Add a robot."

    log = logging.getLogger(__name__)
    _command_name = 'add robot'


class Remove(SingleCommand):
    "Remove something."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Remove, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
        return parser


class RemovePlayer(Remove):
    "Remove a player."

    log = logging.getLogger(__name__)
    _command_name = 'remove player'


class RemoveRobot(Remove):
    "Remove a robot."

    log = logging.getLogger(__name__)
    _command_name = 'remove robot'


class Start(SingleCommand):
    "Start something."

    log = logging.getLogger(__name__)
    _command_name = 'start'

    def get_parser(self, prog_name):
        parser = super(Start, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1,
            choices=('game'))
        return parser


class Stop(SingleCommand):
    "Stop something."

    log = logging.getLogger(__name__)
    _command_name = 'stop'

    def get_parser(self, prog_name):
        parser = super(Stop, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1,
            choices=('application', 'game'))
        return parser


class AgentApp(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        command = CommandManager('orwell.agent')
        super(AgentApp, self).__init__(
            description='Orwell agent.',
            version='0.0.1',
            command_manager=command,
            )
        Start.register_to(command)
        Stop.register_to(command)
        AddPlayer.register_to(command)
        AddRobot.register_to(command)
        RemovePlayer.register_to(command)
        RemoveRobot.register_to(command)
        self._zmq_context = None
        self._zmq_socket = None

    def build_option_parser(
            self,
            description,
            version,
            argparse_kwargs=None):
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
        self.log.debug('initialize_app')
        import zmq
        self._zmq_context = zmq.Context()
        self._zmq_socket = self._zmq_context.socket(zmq.PUB)
        self._zmq_socket.setsockopt(zmq.LINGER, 1)
        self._zmq_socket.connect("tcp://%s:%i" % (
            self.options.address,
            self.options.port))
        import time
        time.sleep(0.001)

    def send(self, command):
        self.log.debug('send command "%s"' % command)
        self._zmq_socket.send(command)

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = AgentApp()
    return myapp.run(argv)


if ("__main__" == __name__):
    sys.exit(main(sys.argv[1:]))  # pragma: no coverage

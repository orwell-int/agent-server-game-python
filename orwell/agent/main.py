import logging
import sys
import socket

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
        self.app.sendAndReceive(
            self._command_name + ' ' + parsed_args.object[0])


class Set(SingleCommand):
    "Set the property of an object."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
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
        self.app.sendAndReceive(
            ' '.join((
                self._command_name,
                parsed_args.name,
                parsed_args.property,
                parsed_args.value)))


class SetRobot(Set):
    "Set the property of a robot."

    log = logging.getLogger(__name__)

    _command_name = 'set robot'
    _properties = ['video_url', ]


class List(SingleCommand):
    "List something."

    log = logging.getLogger(__name__)
    port = None
    host = socket.gethostbyname(socket.getfqdn())

    def take_action(self, parsed_args):
        message = self.app.sendAndReceive(self._command_name)
        self.log.info(message)


class ListPlayer(List):
    "List all players."

    log = logging.getLogger(__name__)
    _command_name = 'list player'


class ListRobot(List):
    "List all robots."

    log = logging.getLogger(__name__)
    _command_name = 'list robot'


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
            choices=('game',))
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


class RegisterRobot(SingleCommand):
    "Register a robot"

    log = logging.getLogger(__name__)
    _command_name = 'register robot'

    def get_parser(self, prog_name):
        parser = super(RegisterRobot, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
        return parser


class UnregisterRobot(SingleCommand):
    "Unregister a robot"

    log = logging.getLogger(__name__)
    _command_name = 'unregister robot'

    def get_parser(self, prog_name):
        parser = super(UnregisterRobot, self).get_parser(prog_name)
        parser.add_argument(
            'object',
            nargs=1)
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
        ListPlayer.register_to(command)
        ListRobot.register_to(command)
        AddPlayer.register_to(command)
        AddRobot.register_to(command)
        RemovePlayer.register_to(command)
        RemoveRobot.register_to(command)
        RegisterRobot.register_to(command)
        UnregisterRobot.register_to(command)
        SetRobot.register_to(command)
        self._zmq_context = None
        self._zmq_request_socket = None

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
        parser.add_argument(
            '-l',
            '--listen',
            type=int,
            default=9004,
            help='The port to listen to for replies.')
        return parser

    def initialize_app(self, argv):
        self.log.debug('initialize_app ; argv = ' + str(argv))
        import zmq
        self._zmq_context = zmq.Context()
        self.log.debug('created context = %s' % self._zmq_context)
        self._zmq_request_socket = self._zmq_context.socket(zmq.REQ)
        self.log.debug(
            'created request socket = %s' % self._zmq_request_socket)
        self._zmq_request_socket.setsockopt(zmq.LINGER, 1)
        self._zmq_request_socket.connect("tcp://%s:%i" % (
            self.options.address,
            self.options.port))
        List.port = str(self.options.listen)
        # if we do not wait the first messages are lost
        import time
        time.sleep(0.6)

    def sendAndReceive(self, command):
        self.log.debug('send command "%s"' % command)
        self.log.debug('call socket.send("%s")' % command)
        self._zmq_request_socket.send(command)
        message = self._zmq_request_socket.recv()
        self.log.debug('received: %s', message)
        return message

    #def receive(self):
        #self.log.debug('try to receive a message')
        #message = self._zmq_request_socket.recv()
        #self.log.debug('received: %s', message)
        #return message

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

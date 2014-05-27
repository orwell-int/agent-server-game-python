from nose.tools import assert_equal
#from nose.tools import assert_true
#from nose.tools import assert_false
from nose.tools import assert_raises
import unittest
import mock
import orwell.agent.main as thougt_police
import pprint


class MainTest(unittest.TestCase):
    def test_1(self):
        thougt_police.main()

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_2(self, zmq_context, zmq_socket):
        thougt_police.main(["stop", "application"])
        found = list(zmq_socket.mock_calls)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(found)
        assert_equal(found[0], mock.call())
        # this does not work
        #assert_equal(found[1], mock.call().__str__())
        assert_equal(found[2], mock.call().socket(1))
        assert_equal(found[4], mock.call().socket().setsockopt(17, 1))
        assert_equal(
            found[5],
            mock.call().socket().connect('tcp://127.0.0.1:9003'))
        assert_equal(found[6], mock.call().socket(7))
        assert_equal(found[8], mock.call().socket().setsockopt(17, 1))
        assert_equal(
            found[9],
            mock.call().socket().bind('tcp://0.0.0.0:9004'))
        assert_equal(
            found[10],
            mock.call().socket().send('stop application'))

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_2_bis(self, zmq_context, zmq_socket):
        thougt_police.main(
            ["-p", "12", "-a", "127.0.0.1", "-l", "42", "stop", "application"])
        found = list(zmq_socket.mock_calls)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(found)
        assert_equal(found[0], mock.call())
        # this does not work
        #assert_equal(found[1], mock.call().__str__())
        assert_equal(found[2], mock.call().socket(1))
        assert_equal(found[4], mock.call().socket().setsockopt(17, 1))
        assert_equal(
            found[5],
            mock.call().socket().connect('tcp://127.0.0.1:12'))
        assert_equal(found[6], mock.call().socket(7))
        assert_equal(found[8], mock.call().socket().setsockopt(17, 1))
        assert_equal(
            found[9],
            mock.call().socket().bind('tcp://0.0.0.0:42'))
        assert_equal(
            found[10],
            mock.call().socket().send('stop application'))

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_3(self, zmq_context, zmq_socket):
        assert_raises(SystemExit, thougt_police.main, ["start", "application"])

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_4(self, zmq_context, zmq_socket):
        thougt_police.main(["stop", "game"])
        assert_equal(
            list(zmq_socket.mock_calls)[-1],
            mock.call().socket().send("stop game"))

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_5(self, zmq_context, zmq_socket):
        thougt_police.main(["add", "player", "toto"])
        assert_equal(
            list(zmq_socket.mock_calls)[-1],
            mock.call().socket().send("add player toto"))
        thougt_police.main(["remove", "player", "toto"])
        assert_equal(
            list(zmq_socket.mock_calls)[-1],
            mock.call().socket().send("remove player toto"))
        thougt_police.main(["add", "robot", "Robert"])
        assert_equal(
            list(zmq_socket.mock_calls)[-1],
            mock.call().socket().send("add robot Robert"))
        thougt_police.main(["remove", "robot", "Robert"])
        assert_equal(
            list(zmq_socket.mock_calls)[-1],
            mock.call().socket().send("remove robot Robert"))

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_6(self, zmq_context, zmq_socket):
        '''
        There is something wrong with this test as some extra calls to
        call().socket().recv().__str__() are added (it seems to be a side
        effect of the mock).
        '''
        thougt_police.main(["list", "robot"])
        import socket
        address = socket.gethostbyname(socket.getfqdn())
        found = list(zmq_socket.mock_calls)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(found)
        assert_equal(
            list(zmq_socket.mock_calls)[-14],
            mock.call().socket().send("list robot {} 9004".format(
                address)))
        assert_equal(
            list(zmq_socket.mock_calls)[-13],
            mock.call().socket().recv())
        thougt_police.main(["list", "player"])
        found = list(zmq_socket.mock_calls)
        pp.pprint(found)
        assert_equal(
            list(zmq_socket.mock_calls)[-15],
            mock.call().socket().send("list player {} 9004".format(
                address)))
        assert_equal(
            list(zmq_socket.mock_calls)[-14],
            mock.call().socket().recv())

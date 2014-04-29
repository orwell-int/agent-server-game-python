from nose.tools import assert_equal
#from nose.tools import assert_true
#from nose.tools import assert_false
from nose.tools import assert_raises
import unittest
import mock
import orwell.agent.main as thougt_police


class MainTest(unittest.TestCase):
    def test_1(self):
        thougt_police.main()

    @mock.patch('zmq.Context')
    @mock.patch('zmq.Socket')
    def test_2(self, zmq_context, zmq_socket):
        thougt_police.main(["stop", "application"])
        found = list(zmq_socket.mock_calls)
        assert_equal(found[0], mock.call())
        # this does not work
        #assert_equal(found[1], mock.call().__str__())
        assert_equal(found[2], mock.call().socket(1))
        assert_equal(found[4], mock.call().socket().setsockopt(17, 1))
        assert_equal(
            found[5],
            mock.call().socket().connect('tcp://127.0.0.1:9003'))
        assert_equal(
            found[6],
            mock.call().socket().send('stop application'))

    @mock.patch('zmq.Context')
    @mock.patch('zmq.Socket')
    def test_2_bis(self, zmq_context, zmq_socket):
        thougt_police.main(
            ["-p", "12", "-a", "localhost", "stop", "application"])
        found = list(zmq_socket.mock_calls)
        assert_equal(found[0], mock.call())
        # this does not work
        #assert_equal(found[1], mock.call().__str__())
        assert_equal(found[2], mock.call().socket(1))
        assert_equal(found[4], mock.call().socket().setsockopt(17, 1))
        assert_equal(
            found[5],
            mock.call().socket().connect('tcp://localhost:12'))
        assert_equal(
            found[6],
            mock.call().socket().send('stop application'))

    @mock.patch('zmq.Context')
    @mock.patch('zmq.Socket')
    def test_3(self, zmq_context, zmq_socket):
        assert_raises(SystemExit, thougt_police.main, ["start", "application"])

    @mock.patch('zmq.Context')
    @mock.patch('zmq.Socket')
    def test_4(self, zmq_context, zmq_socket):
        thougt_police.main(["stop", "game"])
        assert_equal(
            list(zmq_socket.mock_calls)[-1],
            mock.call().socket().send("stop game"))

    @mock.patch('zmq.Context')
    @mock.patch('zmq.Socket')
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

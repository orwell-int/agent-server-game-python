from nose.tools import assert_equal
#from nose.tools import assert_true
#from nose.tools import assert_false
from nose.tools import assert_raises
import unittest
import mock
import orwell.agent.main as thougt_police
import pprint
import zmq


class MainTest(unittest.TestCase):
    def _clean(self, array):
        # it seems that calling the tests add a few unwanted calls to the stack
        return [x for x in array if not str(x).endswith('.__str__()')]

    def test_1(self):
        # without this empty command the program hangs waiting for input
        thougt_police.main([""])

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_2(self, zmq_context, zmq_socket):
        thougt_police.main(["stop", "application"])
        found = self._clean(list(zmq_socket.mock_calls))
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(found)
        assert_equal(found[0], mock.call())
        assert_equal(found[1], mock.call().socket(zmq.REQ))
        assert_equal(found[2], mock.call().socket().setsockopt(zmq.LINGER, 1))
        assert_equal(
            found[3],
            mock.call().socket().connect('tcp://127.0.0.1:9003'))
        assert_equal(
            found[4],
            mock.call().socket().send('stop application'))
        assert_equal(
            found[5],
            mock.call().socket().recv())

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_2_bis(self, zmq_context, zmq_socket):
        thougt_police.main(
            ["-p", "12", "-a", "127.0.0.1", "stop", "application"])
        found = self._clean(list(zmq_socket.mock_calls))
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(found)
        assert_equal(found[0], mock.call())
        assert_equal(found[1], mock.call().socket(zmq.REQ))
        assert_equal(found[2], mock.call().socket().setsockopt(zmq.LINGER, 1))
        assert_equal(
            found[3],
            mock.call().socket().connect('tcp://127.0.0.1:12'))
        assert_equal(
            found[4],
            mock.call().socket().send('stop application'))

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_3(self, zmq_context, zmq_socket):
        assert_raises(SystemExit, thougt_police.main, ["start", "application"])

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_4(self, zmq_context, zmq_socket):
        thougt_police.main(["stop", "game"])
        found = self._clean(list(zmq_socket.mock_calls))
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(found)
        assert_equal(
            found[-2],
            mock.call().socket().send("stop game"))

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_5(self, zmq_context, zmq_socket):
        '''
        There is something wrong with this test as some extra calls to
        call().socket().recv().__str__() are added (it seems to be a side
        effect of the mock).
        '''
        thougt_police.main(["list", "robot"])
        found = self._clean(list(zmq_socket.mock_calls))
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(found)
        assert_equal(
            found[-2],
            mock.call().socket().send("list robot"))
        assert_equal(
            found[-1],
            mock.call().socket().recv())
        thougt_police.main(["list", "player"])
        found = self._clean(list(zmq_socket.mock_calls))
        pp.pprint(found)
        assert_equal(
            found[-2],
            mock.call().socket().send("list player"))
        assert_equal(
            found[-1],
            mock.call().socket().recv())

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_6(self, zmq_context, zmq_socket):
        thougt_police.main(["add", "player", "toto"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("add player toto"))
        thougt_police.main(["remove", "player", "toto"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("remove player toto"))
        thougt_police.main(["add", "robot", "Robert"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("add robot Robert"))
        thougt_police.main(["remove", "robot", "Robert"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("remove robot Robert"))
        thougt_police.main(["register", "robot", "Robert"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("register robot Robert"))
        thougt_police.main(["unregister", "robot", "Robert"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("unregister robot Robert"))
        thougt_police.main(
            ["set", "robot", "Robert", "video_url", "wrong"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("set robot Robert video_url wrong"))
        thougt_police.main(["remove", "robot", "Robert"])
        assert_equal(
            self._clean(list(zmq_socket.mock_calls))[-2],
            mock.call().socket().send("remove robot Robert"))

    @mock.patch('zmq.Context', autospec=True)
    @mock.patch('zmq.Socket', autospec=True)
    def test_7(self, zmq_context, zmq_socket):
        assert_raises(
            SystemExit,
            thougt_police.main,
            ["set", "robot", "Louis", "number", "XIV"])

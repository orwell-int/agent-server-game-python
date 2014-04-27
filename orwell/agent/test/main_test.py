from nose.tools import assert_equal
from nose.tools import assert_true
from nose.tools import assert_false
import unittest
import orwell.agent.main as thougt_police


class Main(unittest.TestCase):
    def test_1(self):
        thougt_police.main()

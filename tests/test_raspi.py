import unittest
from randomboye import raspi


class TestRaspberryPi(unittest.TestCase):

    def setUp(self):
        self.pi1 = raspi.RaspberryPi()

    def tearDown(self):
        pass

    def test_bogus(self):
        self.assertEqual(self.pi1.bogus(), "bogus")

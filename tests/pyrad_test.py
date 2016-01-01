import unittest
import mock
from RadiusLibrary import RadiusLibrary, AcctPacketAdapter, AuthPacketAdapter
import pyrad

class Acct(unittest.TestCase):
    def setUp(self):
        self.radius = AuthPacketAdapter(secret='secret',dict=pyrad.dictionary.Dictionary('dictionary'))

    def test_packet_object(self):
        self.assertIsInstance(self.radius, AuthPacketAdapter)
        self.radius['Acct-Status-Type'] = 'Start'

        self.assertEqual(self.radius, {})

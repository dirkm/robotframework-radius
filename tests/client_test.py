import unittest
import mock
from RadiusClientLibrary import RadiusClientLibrary

def fun(x):
    return x + 1

class MyTest(unittest.TestCase):
    def init_test(self):
        client = RadiusClientLibrary()
        session = client.create_session('client',u'127.0.0.1',u'1812','mysecret','dictionary')
        self.assertEqual(session['address'], '127.0.0.1')
        self.assertEqual(session['port'], 1812)
        self.assertEqual(session['secret'], 'mysecret')
        self.assertEqual(session['dictionary'], 'dictionary')


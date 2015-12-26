import unittest
import mock
from RadiusClientLibrary import RadiusClientLibrary

def fun(x):
    return x + 1

class Auth(unittest.TestCase):
    def accept_test(self):
        radius = RadiusClientLibrary()
        client = radius.create_session('client',u'127.0.0.1',u'1812',u'mysecret','dictionary')
        self.assertEqual(client['address'], '127.0.0.1')
        self.assertEqual(client['port'], 1812)
        self.assertEqual(client['secret'], 'mysecret')
        self.assertEqual(client['dictionary'], 'dictionary')
        sock_mock = mock.MagicMock()
        radius._cache['client']['sock'].sendto = sock_mock
        radius.send_request(u'client',u'AccessRequest',{u'User-Name':u'Mike'})
        a = sock_mock.call_args
        print a

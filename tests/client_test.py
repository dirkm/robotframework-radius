import unittest
import mock
from RadiusLibrary import RadiusLibrary
import pyrad

class Auth(unittest.TestCase):
    def setUp(self):
        self.radius = RadiusLibrary()
        self.client = self.radius.create_client(u'client',u'127.0.0.1',u'1812',u'mysecret',u'dictionary')
        self.server = self.radius.create_server(u'server',u'127.0.0.1',u'1812',u'mysecret',u'dictionary')

    def test_create(self):
        client = self.client

        self.assertEqual(client['address'], '127.0.0.1')
        self.assertIsInstance(client['address'], str)

        self.assertEqual(client['port'], 1812)
        self.assertIsInstance(client['port'], int)

        self.assertEqual(client['secret'], 'mysecret')
        self.assertIsInstance(client['secret'], str)

        self.assertIsInstance(client['dictionary'], pyrad.dictionary.Dictionary)

        #sock_mock = mock.MagicMock()
        #radius._cache['client']['sock'].sendto = sock_mock
        #radius.send_request(u'client',u'AccessRequest',{u'User-Name':u'Mike'})
        #a = sock_mock.call_args

    def test_create_request(self):
        req = self.radius.create_access_request()
        self.assertEqual(req.code, 1)
        self.assertEqual(req.authenticator,None)

    def test_add_request_attributes(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        self.assertEqual(req[1],['user1'])
        self.assertEqual(req['User-Name'],['user1'])
        self.radius.add_request_attribute(u'User-Name','user2')
        self.assertEqual(req['User-Name'],['user1','user2'])

    def test_add_request_encrypt(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        self.radius.add_request_attribute(u'User-Password',u'passwd',crypt=False)
        self.assertEqual(req['User-Password'],[u'passwd'])
    def test_client_send(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        send_req = self.radius.send_request()
        self.assertEqual(send_req.items(),req.items())

    def test_server_receive(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        send_req = self.radius.send_request()
        server_req = self.radius.receive_access_request()

    def test_server_response(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        send_req = self.radius.send_request()
        server_req = self.radius.receive_access_request()
        self.radius.request_should_contain_attribute('User-Name')
        self.radius.create_access_accept()
        self.radius.add_response_attribute('Framed-IP-Address','192.168.121.1')
        self.radius.send_response()
        self.radius.receive_access_accept()
        self.radius.response_should_contain_attribute('Framed-IP-Address')
        self.radius.response_should_contain_attribute('Framed-IP-Address','192.168.121.1')

class Acct(unittest.TestCase):
    def setUp(self):
        self.radius = RadiusLibrary()
        self.client = self.radius.create_client(u'client',u'127.0.0.1',u'1813',u'mysecret',u'dictionary')
        self.server = self.radius.create_server(u'server',u'127.0.0.1',u'1813',u'mysecret',u'dictionary')

    def test_create_request(self):
        req = self.radius.create_accounting_request()
        self.assertEqual(req.code, 4)
        self.assertEqual(req.authenticator,None)

    def test_add_request_attributes(self):
        req = self.radius.create_accounting_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        self.assertEqual(req[1],['user1'])
        self.assertEqual(req['User-Name'],['user1'])
        self.radius.add_request_attribute(u'User-Name','user2')
        self.assertEqual(req['User-Name'],['user1','user2'])

    def test_client_send(self):
        req = self.radius.create_accounting_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        send_req = self.radius.send_request()
        self.assertEqual(send_req.items(),req.items())

    def test_server_receive(self):
        req = self.radius.create_accounting_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        send_req = self.radius.send_request()
        server_req = self.radius.receive_accounting_request()

    def test_server_response(self):
        req = self.radius.create_accounting_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        send_req = self.radius.send_request()
        server_req = self.radius.receive_accounting_request()
        self.radius.create_accounting_response()
        self.radius.add_response_attribute('Framed-IP-Address','192.168.121.1')
        self.radius.send_response()
        self.radius.receive_accounting_response()
#    def test_send(self):
#        attributes = {u'User-Name': u'user'}
#        pkt = self.radius.send_access_request(**attributes)
#        self.assertEqual(pkt['User-Name'], ['user'])
#
#    def test_receive(self):
#        request_attributes = {u'User-Name': u'user'}
#
#        cpkt = self.radius.send_access_request(**request_attributes)
#        spkt = self.radius.receive_access_request()
#        self.assertEqual(cpkt.items(),spkt.items())
#
#        srpkt = self.radius.send_access_accept(**{'Reply-Message':'ok'})
#        crpkt = self.radius.receive_access_accept()
#        self.assertEqual(crpkt.items(),srpkt.items())
#
#    def test_multiple_attribute_values(self):
#        attributes={u'User-Name':[u'user1',u'user2']}
#        pkt = self.radius.send_access_request(**attributes)
#        self.assertEqual(pkt['User-Name'],[u'user1',u'user2'])
#
#    def test_encrypt_type_1_should_auto_crypt(self):
#        srv = self.radius.create_server('server', '127.0.0.1', '1812','mysecret',u'dictionary')
#        attributes = {u'User-Password': u'password'}
#        pkt = self.radius.send_access_request(**attributes)
#        decode = AuthPacketAdapter(secret='mysecret',dict=pyrad.dictionary.Dictionary('dictionary'),packet=pkt.RequestPacket())
#        self.assertIsInstance(decode, AuthPacketAdapter)
#        self.assertIn(u'password', decode['User-Password'])
#
#    def test_encrypt_type_2_should_set_get_raw(self):
#        srv = self.radius.create_server('server', '127.0.0.1', '1812','mysecret',u'dictionary')
#        attributes = {u'ERX-LI-Action': 1}
#        pkt = self.radius.send_access_request(**attributes)
#        decode = AuthPacketAdapter(secret='mysecret',dict=pyrad.dictionary.Dictionary('dictionary'),packet=pkt.RequestPacket())
#        self.assertIsInstance(decode, AuthPacketAdapter)
#        self.assertIn(1, decode[u'ERX-LI-Action'])
#
#class Acct(unittest.TestCase):
#    def setUp(self):
#        self.radius = RadiusLibrary()
#        self.client = self.radius.create_client(u'client',u'127.0.0.1',u'1812',u'mysecret',u'dictionary')
#        self.server = self.radius.create_server(u'server',u'127.0.0.1',u'1812',u'mysecret',u'dictionary')
#
#    def test_multiple_attribue_values(self):
#        attributes={u'User-Name':[u'user1',u'user2'],u'Acct-Status-Type':'Start'}
#        pkt = self.radius.send_accounting_request(**attributes)
#        self.assertEqual(pkt['User-Name'],[u'user1',u'user2'])
#
#    def test_accounting(self):
#        request_attributes = {u'Acct-Status-Type':  'Start'}
#
#        cpkt = self.radius.send_accounting_request(**request_attributes)
#        spkt = self.radius.receive_accounting_request(**request_attributes)
#
#
#        srpkt = self.radius.send_accounting_response()
#        crpkt = self.radius.receive_accounting_response()
#
#        self.assertEqual(crpkt.items(),srpkt.items())
#        self.assertEqual(crpkt.code,srpkt.code)

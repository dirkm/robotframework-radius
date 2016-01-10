import unittest
import mock
from RadiusLibrary import RadiusLibrary
import pyrad
import pyrad.packet

class Auth(unittest.TestCase):
    def setUp(self):
        self.radius = RadiusLibrary()
        self.client = self.radius.create_client(u'client',u'127.0.0.1',u'1812',u'mysecret',u'dictionary')
        self.server = self.radius.create_server(u'server',u'127.0.0.1',u'1812',u'mysecret',u'dictionary')

    def test_create_client(self):
        client = self.client

        self.assertEqual(client['address'], '127.0.0.1')
        self.assertIsInstance(client['address'], str)
        self.assertEqual(client['port'], 1812)
        self.assertIsInstance(client['port'], int)
        self.assertEqual(client['secret'], 'mysecret')
        self.assertIsInstance(client['secret'], str)
        self.assertIsInstance(client['dictionary'], pyrad.dictionary.Dictionary)


    def test_create_request(self):
        for req_type in [('access',pyrad.packet.AccessRequest),
                        ('accounting',pyrad.packet.AccountingRequest),
                        ('coa',pyrad.packet.CoARequest)]:
            req = getattr(self.radius,'create_{}_request'.format(req_type[0]))()
            self.assertEqual(req.code, req_type[1])
            self.assertEqual(req.authenticator,None)
            self.assertIsInstance(req.id,int)

    def test_add_request_attributes_type_string(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        self.assertEqual(req['User-Name'],['user1'])

    def test_add_request_attributes_type_integer(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'NAS-Port',1)
        self.assertEqual(req['NAS-Port'],[1])
        self.radius.add_request_attribute(u'Session-Timeout',u'1')
        self.assertEqual(req['Session-Timeout'],[1])

    def test_add_request_attributes_type_octets(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'Class',u'\x56xx')
        self.assertEqual(req['Class'],['\x56xx'])

    def test_add_request_attributes_type_ipaddr(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'Framed-IP-Address',u'10.0.0.1')
        self.assertEqual(req['Framed-IP-Address'],['10.0.0.1'])

    def test_add_request_encrypted_attribute(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Password',u'passwd',crypt=True)
        self.assertEqual(req.PwDecrypt(req[2].pop()),'passwd')

    def test_send_request(self):
        req = self.radius.create_access_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        self.radius.add_request_attribute(u'User-Password',u'password')
        sock_mock = mock.MagicMock()
        client = self.radius._get_session(self.radius._client,'client')
        client['sock'].sendto = sock_mock
        send_req = self.radius.send_request()
        self.assertEqual(sock_mock.call_args[0][0],req.RequestPacket())

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
        self.radius.request_should_contain_attribute(u'User-Name')
        resp = self.radius.create_access_accept()
        self.assertEqual(resp.code,2)

        self.radius.add_response_attribute(u'Framed-IP-Address',u'192.168.121.1')
        self.assertEqual(resp['Framed-IP-Address'],['192.168.121.1'])
        self.radius.send_response()
        client_rcv = self.radius.receive_access_accept()
        self.assertEqual(client_rcv['Framed-IP-Address'],['192.168.121.1'])
        self.radius.response_should_contain_attribute(u'Framed-IP-Address')
        #self.radius.response_should_contain_attribute('Framed-IP-Address',u'192.168.121.1')

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
        send_req = self.radius.send_request()
        server_req = self.radius.receive_accounting_request()

    def test_server_response(self):
        req = self.radius.create_accounting_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        send_req = self.radius.send_request()
        server_req = self.radius.receive_accounting_request()
        resp = self.radius.create_accounting_response()
        self.radius.add_response_attribute('Framed-IP-Address','192.168.121.1')
        #print resp['Framed-IP-Address']
        self.radius.send_response()
        self.radius.receive_accounting_response()


    def test_coa_request(self):
        req = self.radius.create_coa_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        self.radius.add_request_attribute('Acct-Session-Id', '20')
        self.assertEqual(req.code, pyrad.packet.CoARequest)

    def test_coa_req_receive(self):
        req = self.radius.create_coa_request()
        self.radius.add_request_attribute(u'User-Name',u'user1')
        self.radius.add_request_attribute('Acct-Session-Id', '20')
        self.assertEqual(req.code, pyrad.packet.CoARequest)
        self.radius.send_request()
        req_recv = self.radius.receive_coa_request()
        self.radius.request_should_contain_attribute(u'User-Name')
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

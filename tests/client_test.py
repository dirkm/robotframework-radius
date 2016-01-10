import unittest
import mock
import RadiusLibrary
from RadiusLibrary import RadiusLibrary as RL
import pyrad
import pyrad.packet

class Client(unittest.TestCase):
    def setUp(self):
        self.radius = RL()
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
        self.radius.add_request_attribute(u'User-Password',u'passwd')
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

    @mock.patch('RadiusLibrary.radiuslibrary.select')
    def test_receive_response(self,mock_select):
        client = self.radius._get_session(self.radius._client,'client')
        dictionary = dict=pyrad.dictionary.Dictionary('dictionary')
        acc_resp = pyrad.packet.AcctPacket(code=pyrad.packet.AccountingResponse,
                                           secret='secret',
                                           dict=dictionary)
        acc_resp.authenticator = pyrad.packet.Packet.CreateAuthenticator()
        pdu = acc_resp.ReplyPacket()
        mock_recvfrom = mock.MagicMock(return_value=(pdu,('127.0.0.1',50000)))
        mock_select.return_value=[True]
        client['sock'].recvfrom = mock_recvfrom

        req = self.radius.receive_accounting_response()
        self.assertEqual(req.code,pyrad.packet.AccountingResponse)

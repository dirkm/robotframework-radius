"""RobotFramework Radius Module"""
import select
import socket
from pyrad import packet, dictionary
import six
import robot
from robot.libraries.BuiltIn import BuiltIn

class RadiusLibrary(object):
    """Main Class"""

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self):
        self._cache = robot.utils.ConnectionCache('No Sessions Created')
        self.builtin = BuiltIn()

    def create_client(self, alias, address, port,
                      secret, raddict='dictionary',
                      authenticator=True):
        """Creates client"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        sock.settimeout(3.0)
        sock.setblocking(0)
        session = {'sock': sock,
                   'address': address,
                   'port': int(port),
                   'secret': six.b(str(secret)),
                   'dictionary': dictionary.Dictionary(raddict),
                   'authenticator': authenticator}

        self._cache.register(session, alias=alias)
        return session

    def send_request(self, alias, code, attributes):
        """Sends radius request"""
        session = self._cache.switch(alias)
        authenticator = None
        if session['authenticator']:
            authenticator = packet.Packet.CreateAuthenticator()
        if attributes.has_key('User-Password'):
            attributes['User-Password'] = six.b(attributes['User-Password'])
        if getattr(packet, code) in [packet.AccessRequest]:
            radp = packet.AuthPacket(code=getattr(packet, code),
                                     secret=session['secret'],
                                     dict=session['dictionary'],
                                     authenticator=authenticator)
        elif getattr(packet, code) in [packet.AccountingRequest]:
            radp = packet.AcctPacket(code=getattr(packet, code),
                                     secret=session['secret'],
                                     dict=session['dictionary'],
                                     authenticator=authenticator)
        for (key, val) in attributes.items():
            if key == u'User-Password':
                radp[str(key)] = radp.PwCrypt(str(val))
            else:
                if isinstance(key, unicode):
                    radp[str(key)] = val
                else:
                    radp[key] = val

        raw = radp.RequestPacket()
        session['sock'].sendto(raw, (session['address'], session['port']))
        return radp

    def receive_response(self, alias, code, timeout=15):
        """Receives Response"""
        session = self._cache.switch(alias)
        ready = select.select([session['sock']], [], [], float(timeout))
        if ready[0]:
            data, _ = session['sock'].recvfrom(1024)
            radp = packet.Packet(secret=session['secret'],
                                 packet=data,
                                 dict=session['dictionary'])
            if radp.code != getattr(packet, code):
                raise Exception("received {}", format(radp.code))
        else:
            raise Exception("Did not receive any answer")
        return radp

    def create_server(self, alias, address, port, secret, raddict='dictionary'):
        """Creates Radius Server"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((address, int(port)))
        #sock.settimeout(3.0)
        sock.setblocking(0)
        server = {'sock': sock,
                  'secret': six.b(str(secret)),
                  'dictionary': dictionary.Dictionary(raddict)}
        self._cache.register(server, alias=alias)
        return server

    def receive_request(self, alias, code, timeout=15):
        """Receives request"""
        radp = None
        session = self._cache.switch(alias)
        ready = select.select([session['sock']], [], [], float(timeout))
        if ready[0]:
            data, addr = session['sock'].recvfrom(1024)
            radp = packet.Packet(secret=session['secret'],
                                 packet=data,
                                 dict=session['dictionary'])
            if radp.code != getattr(packet, code):
                raise Exception("received {}", format(radp.code))
        if radp is None:
            raise Exception("Did not receive any answer")
        radp.addr = addr
        return radp

    def send_response(self, alias, request, code, attr=None):
        """Send Response"""
        session = self._cache.switch(alias)
        reply = request.CreateReply()
        request.code = getattr(packet, code)
        if attr:
            for (key, val) in attr.items():
                reply[key] = val
        raw = request.ReplyPacket()
        session['sock'].sendto(raw, request.addr)

    def should_contain_attribute(self, pckt, key=None,val=None):
        """Test if attribute exists"""

        if key and not val:
            return pckt[key.encode('ascii')]
        if key and val:
            if val in pckt[key.encode('ascii')]:
                return
            else:
                raise BaseException('value does not match')

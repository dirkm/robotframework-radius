from pyrad import packet,dictionary
import socket
import six
import select
import robot
from robot.libraries.BuiltIn import BuiltIn

class RadiusClientLibrary(object):
    def __init__(self):
        self._cache = robot.utils.ConnectionCache('No Sessions Created')
        self.builtin = BuiltIn()

    def create_session(self, alias, address, port, secret, dictionary='dictionary'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('',0))
        sock.settimeout(3.0)
        sock.setblocking(0)
        session= { 'sock': sock,
                   'address': address,
                   'port': port,
                   'secret': six.b(str(secret)),
                   'dictionary': dictionary}
        self._cache.register(session, alias=alias)
        return session

    def send_request(self, alias, code, attributes):
        session = self._cache.switch(alias)

        
        if getattr(packet,code) in [packet.AccessRequest]:
          p = packet.AuthPacket(code=getattr(packet,code), secret=session['secret'], dict=dictionary.Dictionary(session['dictionary']))
        elif getattr(packet,code) in [packet.AccountingRequest]:
          p = packet.AcctPacket(code=getattr(packet,code), secret=session['secret'], dict=dictionary.Dictionary(session['dictionary']))

        for (k,v) in attributes.items():
            if k == u'User-Password':
                p[str(k)] = p.PwCrypt(str(v))
            else:
                if type(k) == unicode:
                  p[str(k)] = v
                else:
                  p[k] = v

        raw = p.RequestPacket()
       
        session['sock'].sendto(raw,(session['address'],int(session['port'])))
        
    def receive_response(self, alias, code):
        p = None
        session = self._cache.switch(alias)
        ready = select.select([session['sock']], [], [], 5)
        if ready[0]:
            data, addr = session['sock'].recvfrom(1024)
            self.builtin.log(len(data))
            p = packet.Packet(secret=session['secret'],packet=data,dict=dictionary.Dictionary(session['dictionary']))
            
            if p.code != getattr(packet,code):
                raise Exception("received {}",format(p.code))
        if p == None:
          raise Exception("Did not receive any answer")
        else:
          self.response = p

    def create_server(self, alias, address, port, secret, dictionary='dictionary'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((address,port))
        sock.settimeout(3.0)
        sock.setblocking(0)
        server= { 'sock': sock,
                   'secret': six.b(str(secret)),
                   'dictionary': dictionary}
        self._cache.register(server, alias=alias)
        return server

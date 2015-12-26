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

    def create_session(self, alias, address, port, secret, dictionary='dictionary',authenticator=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('',0))
        sock.settimeout(3.0)
        sock.setblocking(0)
        session= { 'sock': sock,
                   'address': address,
                   'port': int(port),
                   'secret': six.b(str(secret)),
                   'dictionary': dictionary,
                   'authenticator': True }
        self._cache.register(session, alias=alias)
        return session

    create_client = create_session

    def send_request(self, alias, code, attributes):
        session = self._cache.switch(alias)
        authenticator = None
        if session['authenticator']:
            authenticator = packet.Packet.CreateAuthenticator()
        
        if attributes.has_key('User-Password'):
            attributes['User-Password'] = six.b(attributes['User-Password'])
        if getattr(packet,code) in [packet.AccessRequest]:
          p = packet.AuthPacket(code=getattr(packet,code), secret=session['secret'], dict=dictionary.Dictionary(session['dictionary']), authenticator=authenticator)
        elif getattr(packet,code) in [packet.AccountingRequest]:
          p = packet.AcctPacket(code=getattr(packet,code), secret=session['secret'], dict=dictionary.Dictionary(session['dictionary']), authenticator=authenticator)

        for (k,v) in attributes.items():
            if k == u'User-Password':
                p[str(k)] = p.PwCrypt(str(v))
            else:
                self.builtin.log(k)
                if type(k) == unicode:
                  p[str(k)] = v
                else:
                  p[k] = v

        raw = p.RequestPacket()
        session['sock'].sendto(raw,(session['address'],session['port']))
        return p
        
    def receive_response(self, alias, code,timeout=15):
        p = {}
        session = self._cache.switch(alias)
        ready = select.select([session['sock']], [], [], float(timeout))
        if ready[0]:
            data, addr = session['sock'].recvfrom(1024)
            p = packet.Packet(secret=session['secret'],packet=data,dict=dictionary.Dictionary(session['dictionary']))
            self.builtin.log(p.viewitems())
            if p.code != getattr(packet,code):
                raise Exception("received {}",format(p.code))

        else:
            raise Exception("Did not receive any answer")
        return p
        #if type(p) == dict:
        #  raise Exception("Did not receive any answer")
        

    def create_server(self, alias, address, port, secret, dictionary='dictionary'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((address,int(port)))
        #sock.settimeout(3.0)
        sock.setblocking(0)
        server= { 'sock': sock,
                   'secret': six.b(str(secret)),
                   'dictionary': dictionary}
        self._cache.register(server, alias=alias)
        return server

    def receive_request(self, alias, code,timeout=15):
        p = None
        session = self._cache.switch(alias)
        ready = select.select([session['sock']], [], [], float(timeout))
        if ready[0]:
            data, addr = session['sock'].recvfrom(1024)
            p = packet.Packet(secret=session['secret'],packet=data,dict=dictionary.Dictionary(session['dictionary']))
            
            if p.code != getattr(packet,code):
                raise Exception("received {}",format(p.code))
        if p == None:
          raise Exception("Did not receive any answer")
        p.addr = addr
        return p

    def send_response(self,alias,p,code,attr={}):
        self.builtin.log(p)
        session = self._cache.switch(alias)
        reply = p.CreateReply()
        p.code = getattr(packet,code)
        for (k,v) in attr.items():
            print k,v
            reply[k] = v

        
        raw = p.ReplyPacket()
        session['sock'].sendto(raw,p.addr)
        
